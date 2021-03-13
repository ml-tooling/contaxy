<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.api.endpoints.extension`





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `list_extensions`

```python
list_extensions(
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns all installed extensions accesible by the specified project. 

This also includes all extensions which are installed globally as well as extensions installed by the authorized user. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `delete_extension`

```python
delete_extension(
    project_id: str = Path(Ellipsis),
    extension_id: Optional[str] = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Deletes an extension. 

This will delete the installation metadata as well as the service container. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_extension_metadata`

```python
get_extension_metadata(
    project_id: str = Path(Ellipsis),
    extension_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Returns the metadata of the given extension. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `install_extension`

```python
install_extension(
    extension: ExtensionInput,
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Installs an extension for the given project. 

This will deploy the extension container for the selected project and registers the extension for all the specified capabilities. 


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/api/endpoints/extension.py#L108"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `suggest_extension_config`

```python
suggest_extension_config(
    container_image: str = Query(Ellipsis),
    project_id: str = Path(Ellipsis),
    component_manager: ComponentManager = Depends(get_component_manager),
    token: str = Depends(get_api_token)
) → Any
```

Suggests an input configuration based on the provided `container_image`. 

The suggestion is based on metadata extracted from the container image (e.g. labels) as well as suggestions based on previous project deployments with the same image. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
