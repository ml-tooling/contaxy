<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.managers.seed`




**Global Variables**
---------------
- **ERROR_NO_PROJECT_MANAGER**


---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SeedManager`




<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    global_state: Optional[GlobalState] = None,
    request_state: Optional[RequestState] = None,
    auth_manager: Optional[AuthOperations] = None,
    file_manager: Optional[FileOperations] = None,
    project_manager: Optional[ProjectOperations] = None
)
```








---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_file`

```python
create_file(
    project_id: str,
    file_key: str = 'my-test-file',
    max_number_chars: int = 200
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L121"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_file_stream`

```python
create_file_stream(max_number_chars: int = 200) → FileStreamWrapper
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_files`

```python
create_files(
    project_id: str,
    number_of_files: int,
    prefix: Optional[str] = 'my-test-file',
    max_number_chars: int = 200
) → List[File]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_project`

```python
create_project(
    project_input: ProjectCreation = ProjectCreation(display_name='My Test Project!', description=None, icon=None, metadata=None, disabled=False, id='my-test-project')
) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_projects`

```python
create_projects(amount: int) → List[Project]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(
    user_input: UserRegistration = UserRegistration(username='Foo', email='foo@bar.com', disabled=False, password='Foobar')
) → User
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L49"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_users`

```python
create_users(amount: int) → List[User]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/managers/seed.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `setup_user`

```python
setup_user(user: User) → Project
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
