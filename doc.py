from pydantic import  create_model

Model = create_model("Model", __doc__="this is a Model", field=(str, ...))
print(Model.model_json_schema())