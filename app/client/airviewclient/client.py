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
        self._headers = {"Authorization": f"Bearer {backend_config.token}"}
        self._system_id = None

    @property
    def system_id(self):
        if self._system_id is None:
            system_id = self.get_system_id_by_name(self._backend_config.system_name)
            if system_id is None:
                system_id = self.create_system(
                    self._backend_config.system_name, self._backend_config.system_stage
                )
            self._system_id = system_id

        return self._system_id

    def get_system_id_by_name(self, name):
        url = self.get_url(f"/systems/?name={name}")
        resp = self._session.get(url=url, headers=self._headers)
        if resp.status_code == 200:
            data = resp.json()
            return data["id"]
        return None

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
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def get_services(self) -> list[Service]:
        """
        Get a list of services
        """
        url = self.get_url("/services/")
        resp = self._session.get(url=url, headers=self._headers)
        if resp.status_code == 200:
            return [Service(**item) for item in resp.json()]
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def create_service(self, service: Service) -> Service:
        """
        Create a new service
        """

        resp = self._session.post(
            url=self.get_url("/services/"),
            headers=self._headers,
            json={
                "name": service.name,
                "reference": service.reference,
                "type": service.type.name,
            },
        )
        if resp.status_code == 200:
            return Service(**resp.json())
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def create_system(self, name: str, stage: SystemStage) -> Environment:
        """
        Create a new system
        """

        resp = self._session.post(
            url=self.get_url("/systems/"),
            headers=self._headers,
            json={
                "name": name,
                "stage": stage.name,
            },
        )
        if resp.status_code == 200:
            return resp.json()["id"]
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

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
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def get_application_environment_by_reference(self, reference) -> Application | None:
        """
        Look up an application by the provided reference
        """
        type = self._backend_config.referencing_type
        url = self.get_url(
            f"/referenced-application-environments/?type={type}&reference={reference}"
        )
        resp = self._session.get(url=url, headers=self._headers)

        if resp.status_code == 200:
            data = resp.json()
            return Application(
                id=data["application"]["id"],
                name=data["application"]["name"],
                application_environment_id=data["id"],
                reference=reference,
            )
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def create_application(
        self, application: Application, environment_id: int = None
    ) -> Application:
        """
        Create a new Application
        """
        data = {
            "name": application.name,
            "applicationType": application.type.name,
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
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def create_application_environment(self, application: Application) -> Application:
        """
        Create a new Application Environment, returns application environment id
        """
        data = {
            "applicationId": application.id,
            "environmentId": application.environment.id,
            "references": [
                {
                    "type": self._backend_config.referencing_type,
                    "reference": application.reference,
                }
            ],
        }
        resp = self._session.post(
            url=self.get_url("/application-environments/"),
            headers=self._headers,
            json=data,
        )
        if resp.status_code == 200:
            data = resp.json()
            application.application_environment_id = data["id"]
            return application
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def update_application(self, application: Application, environment_id: int) -> None:
        data = {
            "id": application.id,
            "name": application.name,
            "environmentId": environment_id,
            "applicationType": application.type.name,
            "parentId": application.parent_id,
        }
        resp = self._session.put(
            url=self.get_url(f"/applications/{application.id}"),
            headers=self._headers,
            json=data,
        )
        if resp.status_code != 204:
            raise BackendFailureException(
                f"Status code: {resp.status_code} Message: {resp.text}"
            )

    def get_technical_control(self, reference) -> TechnicalControl:
        """
        Get a Technical Control by its reference
        """
        resp = self._session.get(
            url=self.get_url(
                f"/technical-controls/?systemId={self.system_id}&reference={reference}"
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
                control_action=TechnicalControlAction[control["controlAction"]],
                is_blocking=control["isBlocking"],
            )
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def get_control(self, control) -> Optional[Control]:
        resp = self._session.get(
            url=self.get_url(
                f"/controls/?name={control.name}"
            ),
            headers=self._headers,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:
                return None
            control = data[0]
            return Control(
                id=control["id"],
                name=control["name"],
                service_id=control["serviceId"]
            )
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def create_control(self, control) -> Control:
        data = {
            'name': control.name,
            'serviceId': control.service_id,
            'qualityModel': control.quality_model.name,
            'severity': control.severity.name
        }
        resp = self._session.post(
            url=self.get_url(
                f"/controls/"
            ),
            json=data,
            headers=self._headers
        )
        if resp.status_code == 200:
            control = resp.json()
            return Control(
                id=control["id"],
                name=control["name"],
                service_id=control["serviceId"],
                quality_model=control['qualityModel']
            )

        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    

    def save_monitored_resource(self, technical_control_id, resource_id, state) -> None:
        """Persist the current status of a montiored resource"""

        url = self.get_url(
            f"/monitored-resources/?technicalControlId={technical_control_id}&resourceId={resource_id}"
        )
        resp = self._session.put(
            url=url,
            json={
                "monitoringState": state,
            },
            headers=self._headers,
        )
        if resp.status_code != 204:
            raise BackendFailureException(
                f"Status code: {resp.status_code} Message: {resp.text}"
            )

    def create_technical_control(
        self, technical_control: TechnicalControl
    ) -> TechnicalControl:
        mapped = {
            "name": technical_control.name,
            "reference": technical_control.reference,
            "systemId": self.system_id,
            "ttl": technical_control.ttl,
            "isBlocking": technical_control.is_blocking,
            "controlAction": technical_control.control_action.name,
            "controlId": technical_control.control_id
        }
        resp = self._session.post(
            url=self.get_url("/technical-controls/"),
            json={k: v for k, v in mapped.items() if v is not None},
            headers=self._headers,
        )

        if resp.status_code == 200:
            control = resp.json()
            return TechnicalControl(
                id=control["id"],
                name=control["name"],
                reference=control["reference"],
                control_action=TechnicalControlAction[control["controlAction"]],
                is_blocking=control["isBlocking"],
            )

        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

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
                f"/systems/{self.system_id}/exclusion-resources/?state={state.name}"
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

        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

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
            raise BackendFailureException(
                f"Status code: {resp.status_code} Message: {resp.text}"
            )

    def get_resource_id(
        self, reference: str, application_environment_id: int
    ) -> Optional[int]:
        """Get the id of a resource by its application id and reference"""
        resp = self._session.get(
            url=self.get_url(
                f"/resources/?applicationEnvironmentId={application_environment_id}&reference={reference}",
            ),
            headers=self._headers,
        )
        if resp.status_code == 200:
            return resp.json()["id"]
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def create_resource(
        self, reference: str, application_environment_id: int
    ) -> Optional[int]:
        """Create a barebone resource for linking compliance event to"""
        resp = self._session.post(
            url=self.get_url(f"/resources/"),
            headers=self._headers,
            json={
                "name": reference,
                "reference": reference,
                "applicationEnvironmentId": application_environment_id,
            },
        )
        if resp.status_code == 200:
            return resp.json()["id"]

        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )

    def save_resource(self, resource: Resource) -> None:
        """Create a barebone resource for linking compliance event to"""
        resp = self._session.put(
            url=self.get_url(
                f"/resources/?applicationEnvironmentId={resource.application.application_environment_id}&reference={resource.reference}"
            ),
            headers=self._headers,
            json={
                "name": resource.name,
                "reference": resource.reference,
                "applicationEnvironmentId": resource.application.application_environment_id,
                "serviceId": resource.service.id,
            },
        )
        if resp.status_code != 204:
            raise BackendFailureException(
                f"Status code: {resp.status_code} Message: {resp.text}"
            )
        
    def get_framework(self, framework: Framework) -> Optional[Framework]:
        resp = self._session.get(
            url=self.get_url(
                f"/frameworks/?name={framework.name}"
            ),
            headers=self._headers
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:
                return None
            framework.id = data[0]['id']
            return framework
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def create_framework(self, framework: Framework) -> Optional[Framework]:
        resp = self._session.post(
            url=self.get_url(
                f"/frameworks/"
            ),
            json={
                "name": framework.name,
                "link": framework.link
            },
            headers=self._headers
        )
        if resp.status_code == 200:
            framework.id = resp.json()['id']
            return framework
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def get_framework_section(self, framework_section: FrameworkSection) -> Optional[FrameworkSection]:
        resp = self._session.get(
            url=self.get_url(
                f"/frameworks/{framework_section.framework.id}/sections/?name={framework_section.name}"
            ),
            headers=self._headers
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:
                return None
            framework_section.id = data[0]['id']
            return framework_section
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def create_framework_section(self, framework_section: FrameworkSection) -> Optional[FrameworkSection]:
        resp = self._session.post(
            url=self.get_url(
                f"/frameworks/{framework_section.framework.id}/sections/"
            ),
            json={
                "name": framework_section.name,
                "link": framework_section.link,
                "frameworkId": framework_section.framework.id
            },
            headers=self._headers
        )
        if resp.status_code == 200:
            framework_section.id = resp.json()['id']
            return framework_section
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def get_framework_control_objective(self, framework_control_objective: FrameworkControlObjective) -> Optional[FrameworkControlObjective]:
        resp = self._session.get(
            url=self.get_url(
                (
                    f"/frameworks/{framework_control_objective.framework_section.framework.id}/sections"
                    f"/{framework_control_objective.framework_section.id}/control-objectives/?name={framework_control_objective.name}"
                )
            ),
            headers=self._headers
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:  
                return None
            framework_control_objective.id = data[0]['id']
            return framework_control_objective
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def create_framework_control_objective(self, framework_control_objective: FrameworkControlObjective) -> Optional[FrameworkControlObjective]:
        resp = self._session.post(
            url=self.get_url(
                (
                    f"/frameworks/{framework_control_objective.framework_section.framework.id}"
                    f"/sections/{framework_control_objective.framework_section.id}/control-objectives/"
                )
            ),
            json={
                "name": framework_control_objective.name,
                "link": framework_control_objective.link,
                "frameworkSectionId": framework_control_objective.framework_section.id
            },
            headers=self._headers
        )
        if resp.status_code == 200:
            framework_control_objective.id = resp.json()['id']
            return framework_control_objective
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def get_framework_control_objective_link(self, framework_control_objective: FrameworkControlObjective, control: Control) -> Optional[FrameworkControlObjectiveLink]:
        resp = self._session.get(
            url=self.get_url(
                f"/frameworks/framework-control-objective-link/?controlId={control.id}&frameworkControlObjectiveId={framework_control_objective.id}"
            ),
            headers=self._headers
        )
        if resp.status_code == 200:
            data = resp.json()
            if data == []:
                return None
            return FrameworkControlObjectiveLink(
                control_id=data[0]['controlId'],
                framework_control_objective_id=data[0]['frameworkControlObjectiveId'],
                # id=data[0]['id']
            )
        if resp.status_code == 404:
            return None
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )
    
    def create_framework_control_objective_link(self, framework_control_objective: FrameworkControlObjective, control: Control) -> Optional[FrameworkControlObjectiveLink]:
        resp = self._session.post(
            url=self.get_url(
                f"/frameworks/framework-control-objective-link/"
            ),
            json={
                "frameworkControlObjectiveId": framework_control_objective.id,
                "controlId": control.id
            },
            headers=self._headers
        )
        if resp.status_code == 200:
            data = resp.json()
            framework_control_objective_link = FrameworkControlObjectiveLink(
                framework_control_objective_id=framework_control_objective.id,
                control_id=control.id,
                # id=data['id']
            )
            return framework_control_objective_link
        raise BackendFailureException(
            f"Status code: {resp.status_code} Message: {resp.text}"
        )


class Handler:
    """Main helper methods for interacting with AirView"""

    def __init__(self, backend: Backend):
        self._backend = backend

    def handle_resource(self, resource: Resource) -> None:
        # check if env pre-exist
        environments = self._backend.get_environments()
        found_environment = next(
            (
                e
                for e in environments
                if e.abbreviation == resource.application.environment.abbreviation
            ),
            None,
        )
        if found_environment is None:
            found_environment = self._backend.create_environment(
                resource.application.environment
            )

        resource.application.environment = found_environment

        # check app pre-exists
        application = self._backend.get_application_environment_by_reference(
            reference=resource.application.reference
        )

        if application is None:
            # create new app
            application = self._backend.create_application(
                application=resource.application
            )

            application = self._backend.create_application_environment(
                application=resource.application
            )

        all_services = self._backend.get_services()

        service = next(
            (e for e in all_services if e.reference == resource.service.reference),
            None,
        )
        if service is None:
            service = self._backend.create_service(resource.service)

        resource.service.id = service.id
        resource.application.application_environment_id = (
            application.application_environment_id
        )
        self._backend.save_resource(resource)


    def handle_control(self, control: Control) -> Control:
        # check control pre-exists
        backend_control = self._backend.get_control(control)
        # NOTE: We're assuming at this point that a control links to a single service...
        if backend_control is None:
            if control.service_name:
                all_services = self._backend.get_services()
                service = next(
                    (e for e in all_services if e.name == control.service_name),
                    None,
                )
                if service is None:
                    service = self._backend.create_service(Service(
                        name=control.service_name,
                        reference=control.service_name,
                        # NOTE: UNKNOWN will have to do for now.
                        type=ServiceType.UNKNOWN
                    ))
                control.service_id = service.id
            backend_control = self._backend.create_control(
                control
            )
        return backend_control

    def handle_technical_control(
        self, technical_control: TechnicalControl
    ) -> TechnicalControl:
        """When passed a technical control this method will check its existance and if it does not exist a new one will be created. The technical control is returned"""
        # check control pre exists
        backend_techincal_control = self._backend.get_technical_control(
            reference=technical_control.reference
        )
        # create / update parent control
        backend_control = None
        if technical_control.control and ((backend_techincal_control is None) or (backend_techincal_control.control_id is None)):
            backend_control = self.handle_control(technical_control.control)

        if backend_techincal_control == None:
            # create control
            backend_techincal_control = self._backend.create_technical_control(
                technical_control
            )
        if backend_control:
            backend_techincal_control.control_id = backend_control.id
        return backend_techincal_control

    def handle_compliance_event(self, compliance_event: ComplianceEvent) -> None:
        """When passed a compliance event this method will attempt to create any missing defintions for Application and Technical Controls and persist the presented event"""
        # check if env pre-exist
        environments = self._backend.get_environments()
        found_environment = next(
            (
                e
                for e in environments
                if e.abbreviation
                == compliance_event.application.environment.abbreviation
            ),
            None,
        )
        if found_environment is None:
            found_environment = self._backend.create_environment(
                compliance_event.application.environment
            )

        compliance_event.application.environment = found_environment

        # check app pre-exists

        application = self._backend.get_application_environment_by_reference(
            reference=compliance_event.application.reference
        )

        if application is None:
            # create new app
            application = self._backend.create_application(
                application=compliance_event.application
            )

            application = self._backend.create_application_environment(
                application=compliance_event.application
            )

        control = self.handle_technical_control(compliance_event.technical_control)

        # Ensure resource exists
        resource_id = self._backend.get_resource_id(
            application_environment_id=application.application_environment_id,
            reference=compliance_event.resource_reference,
        )
        if resource_id is None:
            resource_id = self._backend.create_resource(
                application_environment_id=application.application_environment_id,
                reference=compliance_event.resource_reference,
            )

        # save triggered
        self._backend.save_monitored_resource(
            technical_control_id=control.id,
            resource_id=resource_id,
            state=compliance_event.status.name,
        )

    def handle_framework_control_objective(self, framework_control_objective: FrameworkControlObjective) -> FrameworkControlObjective:
        backend_framework = self._backend.get_framework(
            framework_control_objective.framework_section.framework
        )
        if backend_framework is None:
            backend_framework = self._backend.create_framework(
                framework_control_objective.framework_section.framework
            )
        framework_control_objective.framework_section.framework.id = backend_framework.id

        backend_framework_section = self._backend.get_framework_section(
            framework_control_objective.framework_section
        )
        if backend_framework_section is None:
            backend_framework_section = self._backend.create_framework_section(
                framework_control_objective.framework_section
            )
        framework_control_objective.framework_section.id = backend_framework_section.id

        backend_framework_control_objective = self._backend.get_framework_control_objective(
            framework_control_objective
        )
        if backend_framework_control_objective is None:
            backend_framework_control_objective = self._backend.create_framework_control_objective(
                framework_control_objective
            )
        framework_control_objective.id = backend_framework_control_objective.id
            
        return framework_control_objective
    

    def handle_framework_control_objective_link(self, framework_control_objective: FrameworkControlObjective, control: Control) -> FrameworkControlObjectiveLink:
        backend_framework_control_objective = self.handle_framework_control_objective(framework_control_objective)
        backend_control = self.handle_control(control)

        framework_control_objective_link = self._backend.get_framework_control_objective_link(
            backend_framework_control_objective, backend_control
        )
        if framework_control_objective_link is None:
            framework_control_objective_link = self._backend.create_framework_control_objective_link(
                backend_framework_control_objective, backend_control
            )
        return framework_control_objective_link


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


def get_oauth_token(
    oauth_endpoint: str,
    client_id: str,
    client_secret: str,
    scope: str,
    additional_headers=None,
) -> str:
    """
    Helper method to get OAuth Token
    :param oauth_endpoint: OAuth Token endpoint
    :param client_id: Client ID
    :param client_secret: Client Secret
    :param scope: OAuth Scope(s)
    :param additional_headers: Addtional HTTP Request Headers
    :return: HTTP Authorization header value
    """
    if additional_headers is None:
        additional_headers = dict()

    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": scope,
    }

    resp = requests.post(url=oauth_endpoint, data=auth_data, headers=additional_headers)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise BackendFailureException(
            f"Failed to get oauth token!  HTTP response: {resp.status_code}"
        )

    d = resp.json()
    token = f"Bearer {d.get('access_token')}"
    return token


def get_azure_token(
    client_id: str, client_secret: str, tenant_id: str, scope: str
) -> str:
    """
    Helper method to get an Azure AD token for use with the client
    :param client_id: Client ID
    :param client_secret: Client Secret
    :param tenant_id: Azure Tenant ID
    :param scope: OAuth Scope
    :return:
    """
    token = get_oauth_token(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token?grant_type=client_credential",
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
    )

    return token


def get_aws_cognito_token(
    client_id: str,
    client_secret: str,
    cognito_pool_domain_prefix: str,
    aws_region: str,
    scope: str = "airview/agent_push",
) -> str:
    """
    Helper method to get an AWS Cognito token for use with the client
    :param client_id: Cognito Client ID
    :param client_secret: Cognito Client Secret
    :param cognito_pool_domain_prefix: Cognito User Pool Domain Name Prefix
    :param aws_region: AWS Region Name
    :param scope: OAuth Scope
    :return: HTTP Authorization header value
    """
    token = get_oauth_token(
        f"https://{cognito_pool_domain_prefix}.auth.{aws_region}.amazoncognito.com/oauth2/token",
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        additional_headers={"content-type": "application/x-www-form-urlencoded"},
    )

    return token


def _get_handler(session: requests.Session, backend_config: BackendConfig):
    backend = Backend(session=session, backend_config=backend_config)
    return Handler(backend)


def get_handler(
    base_url: str,
    system_name: str,
    system_stage: SystemStage,
    referencing_type: str,
    token: str,
) -> Handler:
    """Get an instance of handler using the configuration provided

    :param base_url: The base url at which the AirView API is located
    :param system_name: The unique name which identifies this system
    :param referencing_type: The common reference type which will be used to identify/deduplicate applications e.g. aws_account_id
    :param token: The access token to be used to authenticate with the API
    """

    backed_config = BackendConfig(
        base_url=base_url,
        system_name=system_name,
        system_stage=system_stage,
        referencing_type=referencing_type,
        token=token,
    )
    session = requests.Session()
    return _get_handler(session=session, backend_config=backed_config)
