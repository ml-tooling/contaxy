<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.seed`






---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SeedOperations`







---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_file`

```python
create_file(
    project_id: str,
    file_key: str = 'my-test-file',
    max_number_chars: int = 200
) → File
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L56"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_file_stream`

```python
create_file_stream(max_number_chars: int = 200) → BytesIO
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_files`

```python
create_files(
    project_id: str,
    number_of_files: int,
    prefix: str = 'my-test-file',
    max_number_chars: int = 200
) → List[File]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_project`

```python
create_project(
    project_input: ProjectCreation = ProjectCreation(display_name='My Test Project!', description='', icon=None, metadata={}, disabled=False, id='my-test-project')
) → Project
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_projects`

```python
create_projects(amount: int) → List[Project]
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(
    user_input: UserRegistration = UserRegistration(username='Foo', email='foo@bar.com', disabled=False, password='Foobar')
) → User
```





---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/seed.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_users`

```python
create_users(amount: int) → List[User]
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
