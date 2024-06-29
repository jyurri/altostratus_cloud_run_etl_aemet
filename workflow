main:
  params: [args]
  steps:
  - init:
      assign:
        - repository: projects/data-altostratus/locations/europe-southwest1/repositories/altostratus-data-wheather-transform

  - checkService:
      call: http.get
      args:
        url: "https://aemet-elt-service-omldnfbq4q-no.a.run.app/load_missing_data/"
      result: serviceResponse

  - printStatusCode:
      call: sys.log
      args:
        text: ${"Service response status code " + serviceResponse.code}
        severity: INFO

  - conditionallyExecuteDataform:
      switch:
        - condition: ${serviceResponse.code == 200}
          steps:
            - createCompilationResult:
                call: http.post
                args:
                  url: ${"https://dataform.googleapis.com/v1beta1/" + repository + "/compilationResults"}
                  auth:
                    type: OAuth2
                  body:
                    gitCommitish: main
                result: compilationResult

            - createWorkflowInvocation:
                call: http.post
                args:
                  url: ${"https://dataform.googleapis.com/v1beta1/" + repository + "/workflowInvocations"}
                  auth:
                    type: OAuth2
                  body:
                    compilationResult: ${compilationResult.body.name}
                result: workflowInvocation

            - complete:
                return: ${workflowInvocation.body.name}
