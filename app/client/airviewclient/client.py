from __future__ import annotations
import requests
from .models import *


class Backend:
    """
    Low level wrapper for calls to AirView api.
    THIS CLASS IS INTENDED FOR INTERNAL USE ONLY.

    """

    def __init__(self, backend_config: BackendConfig, session) -> None:
        self.referencing_type = backend_config.referencing_type
        self._session = session
        self._backend_config = backend_config
        self._headers = {"Authorization": backend_config.token}

    def get_url(self, route) -> str:
        """
        Helper method to resolve route to full url
        """
        return f"{self._backend_config.base_url}{route}"

    def get_environments(self) -> list[Environment]:
        """
        Get a list of environments
        """
        url = self.get_url("/environments/")
        resp = self._session.get(url=url, headers=self._headers)
        if resp.status_code == 200:
            return [Environment(**item) for item in resp.json()]
        raise BackendFailureException(f"Status code: {resp.status_code}")

    def create_environment(self, environment: Environment) -> Environment:
        """
        Create a new environment
        """

        resp = self._session.post(
            url=self.get_url("/environments/"),
            headers=self._headers,
            json={
                "name": environment.name,
                "abbreviation": environment.abbreviation,
            },
        )
        if resp.status_code == 200:
            return Environment(**resp.json())
        raise BackendFailureException(f"Status code: {resp.status_code}")

    def get_application_by_reference(self, application_reference) -> Application | None:
        """
        Look up an application by the provided reference
        """
        type = self._backend_config.referencing_type
        url = self.get_url(
            f"/referenced-applications/?type={type}&reference={application_reference}"
        )
        resp = self._session.get(url=url, headers=self._headers)

        if resp.status_code == 200:
            data = resp.json()
            return Application(
                id=data["id"],
                name=data["name"],
                parent_id=data["parentId"],
                reference=application_reference,
            )
        if resp.status_code == 404:
            return None
        raise BackendFailureException(f"Status code: {resp.status_code}")

    def create_application(
        self, application: Application, environment_id: int = None
    ) -> Application:
        """
        Create a new Application
        """
        data = {
            "name": application.name,
            "applicationTypeId": application.type,
            "parentId": application.parent_id,
            "environmentId": environment_id,
            "references": [
                {
                    "type": self._backend_config.referencing_type,
                    "reference": application.reference,
                }
            ],
        }
        resp = self._session.post(
            url=self.get_url("/applications/"),
            headers=self._headers,
            json=data,
        )
        if resp.status_code == 200:
            data = resp.json()
            application.id = resp.json()["id"]
            return application
        raise BackendFailureException(f"Status code: {resp.status_code}")

    def update_application(self, application: Application, environment_id: int) -> None:
        data = {
            "id": application.id,
            "name": application.name,
            "environmentId": environment_id,
            "applicationTypeId": application.type,
            "parentId": application.parent_id,
        }
        resp = self._session.put(
            url=self.get_url(f"/applications/{application.id}"),
            headers=self._headers,
            json=data,
        )
        if resp.status_code != 204:
            raise BackendFailureException(f"Status code: {resp.status_code}")

    def get_technical_control(self, reference) -> TechnicalControl:
        """
        Get a Technical Control by its reference
        """
        resp = self._session.get(
            url=self.get_url(
                f"/technical-controls/?systemId={self._backend_config.system_id}&reference={reference}"
            ),
            headers=self._headers,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:
                return None
            control = data[0]
            return TechnicalControl(
                id=control["id"],
                name=control["name"],
                reference=control["reference"],
                quality_model=QualityModel[control["qualityModel"]],
                type=TechnicalControlType[control["controlType"]],
            )
        raise BackendFailureException(f"Status code: {resp.status_code}")

    def get_application_control_link(
        self, application_id, technical_control_id
    ) -> int | None:
        """Get the id of application to control linkage"""
        url = self.get_url(
            f"/application-technical-controls/?applicationId={application_id}&technicalControlId={technical_control_id}"
        )
        resp = self._session.get(
            url=url,
            headers=self._headers,
        )
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise BackendFailureException(f"Status code: {resp.status_code}")
        return resp.json()["id"]

    def save_monitored_resource(self, app_tech_control_id, reference, state) -> None:
        """Persist the current status of a montiored resource"""

        url = self.get_url(
            f"/monitored-resources/?applicationTechnicalControlId={app_tech_control_id}&reference={reference}"
        )
        resp = self._session.put(
            url=url,
            json={
                "state": state,
            },
            headers=self._headers,
        )
        if resp.status_code != 204:
            raise BackendFailureException(f"Status code: {resp.status_code}")

    def create_technical_control(
        self, technical_control: TechnicalControl
    ) -> TechnicalControl:
        resp = self._session.post(
            url=self.get_url("/technical-controls/"),
            json={
                "name": technical_control.name,
                "reference": technical_control.reference,
                "controlType": technical_control.type.name,
                "qualityModel": technical_control.quality_model.name,
                "systemId": self._backend_config.system_id,
            },
            headers=self._headers,
        )

        if resp.status_code == 200:
            control = resp.json()
            return TechnicalControl(
                id=control["id"],
                name=control["name"],
                reference=control["reference"],
                quality_model=QualityModel[control["qualityModel"]],
                type=TechnicalControlType[control["controlType"]],
            )

        raise BackendFailureException(f"Status code: {resp.status_code}")

    def link_application_to_control(self, application_id, technical_control_id) -> int:
        """create a new linkage between application and technical control"""
        resp = self._session.post(
            url=self.get_url("/application-technical-controls/"),
            json={
                "technicalControlId": technical_control_id,
                "applicationId": application_id,
            },
            headers=self._headers,
        )
        if resp.status_code != 200:
            raise BackendFailureException(f"Status code: {resp.status_code}")
        return resp.json()["id"]

    def _get_application_reference(self, arr):
        for item in arr:
            if item["type"] == self.referencing_type:
                return item["reference"]
        raise Exception("account id not found")

    def get_exclusion_resources(
        self, state: ExclusionResourceState
    ) -> list[ExclusionResource]:
        """Get a list of exclusion resources by state"""
        resp = self._session.get(
            url=self.get_url(
                f"/systems/{self._backend_config.system_id}/exclusion-resources/?state={state.name}"
            ),
            headers=self._headers,
        )
        if resp.status_code == 200:
            return [
                ExclusionResource(
                    id=item["id"],
                    reference=item["reference"],
                    technical_control_reference=item["technicalControlReference"],
                    application_reference=self._get_application_reference(
                        item["applicationReferences"]
                    ),
                    state=ExclusionResourceState[item["state"]],
                )
                for item in resp.json()
            ]

        raise BackendFailureException(f"Status code: {resp.status_code}")

    def set_exclusion_resource_state(
        self, id: int, state: ExclusionResourceState
    ) -> None:
        """Set the state of an exclusion resource"""
        resp = self._session.put(
            url=self.get_url(f"/exclusion-resources/{id}/"),
            headers=self._headers,
            json={"id": id, "state": state.name},
        )
        if resp.status_code != 204:
            raise BackendFailureException(f"Status code: {resp.status_code}")


class Handler:
    """Main helper methods for interacting with AirView"""

    def __init__(self, backend: Backend):
        self._backend = backend

    def handle_application(self, application: Application) -> Application:
        """
        When passed an application definition, this method will attempt to create or update the application definintion.
        Returns application with id present in response
        """
        all_environments = self._backend.get_environments()

        environment = next(
            (
                e
                for e in all_environments
                if e.abbreviation == application.environment.abbreviation
            ),
            None,
        )
        if environment is None:
            environment = self._backend.create_environment(application.environment)

        existing_application = self._backend.get_application_by_reference(
            application_reference=application.reference
        )
        if existing_application is not None:
            # Update app
            application.id = existing_application.id
            application.parent_id = existing_application.parent_id
            self._backend.update_application(
                application=application, environment_id=environment.id
            )
        else:
            # Create new app
            application = self._backend.create_application(
                application=application, environment_id=environment.id
            )

        application.environment.id = environment.id
        application.environment.name = environment.name
        return application

    def handle_compliance_event(self, compliance_event: ComplianceEvent) -> None:
        """When passed a compliance event this method will attempt to create any missing defintions for Application and Technical Controls and persist the presented event"""
        # check app pre-exists
        application = self._backend.get_application_by_reference(
            application_reference=compliance_event.application.reference
        )

        if application is None:
            # create new app
            application = self._backend.create_application(
                application=compliance_event.application, environment_id=None
            )

        # check control pre exists
        control = self._backend.get_technical_control(
            reference=compliance_event.technical_control.reference
        )

        if control == None:
            # create control
            control = self._backend.create_technical_control(
                compliance_event.technical_control
            )

        # ensure control is linked to app
        link_id = self._backend.get_application_control_link(
            application_id=application.id, technical_control_id=control.id
        )
        if link_id is None:
            link_id = self._backend.link_application_to_control(
                application_id=application.id, technical_control_id=control.id
            )

        # save triggered
        self._backend.save_monitored_resource(
            app_tech_control_id=link_id,
            reference=compliance_event.resource_reference,
            state=compliance_event.status.name,
        )

    def set_exclusion_resource_state(
        self, id: int, state: ExclusionResourceState
    ) -> None:
        """Set the status of a exclusion resource

        :param id: The id of the exclusion resource to update
        :param state: The state to set the excusion to
        """

        self._backend.set_exclusion_resource_state(id=id, state=state)

    def get_exclusions_by_state(
        self, state: ExclusionResourceState
    ) -> list[ExclusionResource]:
        """Get a list of exclusion resources filtered by state.

        :param state: The exclusion state to filter by
        """
        items = self._backend.get_exclusion_resources(state)
        return items


def get_azure_token(
    client_id: str, client_secret: str, tenant_id: str, scope: str
) -> str:
    """Helper method to get an Azure AD token for use with the client"""
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": scope,
    }

    resp = requests.post(
        url=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token?grant_type=client_credential",
        data=auth_data,
    )
    d = resp.json()
    token = f"Bearer {d.get('access_token')}"
    return token


def _get_handler(session: requests.Session, backend_config: BackendConfig):
    backend = Backend(session=session, backend_config=backend_config)
    return Handler(backend)


def get_handler(
    base_url: str, system_id: int, referencing_type: str, token: str
) -> Handler:
    """Get an instance of handler using the configuration provided

    :param base_url: The base url at which the AirView API is located
    :param system_id: The pre allocated id which will be used to uniquely identify this system in AirView
    :param referencing_type: The common reference type which will be used to identify/deduplicate applications e.g. aws_account_id
    :param token: The access token to be used to authenticate with the API
    """

    backed_config = BackendConfig(
        base_url=base_url,
        system_id=system_id,
        referencing_type=referencing_type,
        token=token,
    )
    session = requests.Session()
    return _get_handler(session=session, backend_config=backed_config)
