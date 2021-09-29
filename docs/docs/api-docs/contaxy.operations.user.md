<!-- markdownlint-disable -->

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `contaxy.operations.user`
Operations associated with the user handling. 



---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserOperations`
Collection of operations associated with the user handling. 

This interface should be implemented by a user manager. 




---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_user`

```python
create_user(user_input: UserInput, technical_user: bool = False) → User
```

Creates a user. 



**Args:**
 
 - <b>`user_input`</b>:  The user data to create the new user. 
 - <b>`technical_user`</b>:  If `True`, the created user will be marked as technical user. Defaults to `False`. 



**Raises:**
 
 - <b>`ResourceAlreadyExistsError`</b>:  If a user with the same username or email already exists. 



**Returns:**
 
 - <b>`User`</b>:  The created user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_user`

```python
delete_user(user_id: str) → None
```

Deletes a user. 



**Args:**
 
 - <b>`user_id`</b> (str):  The ID of the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_user`

```python
get_user(user_id: str) → User
```

Returns the user metadata for a single user. 



**Args:**
 
 - <b>`user_id`</b>:  The ID of the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 



**Returns:**
 
 - <b>`User`</b>:  The user information. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_users`

```python
list_users() → List[User]
```

Lists all users. 

TODO: Filter based on authenticated user? 



**Returns:**
 
 - <b>`List[User]`</b>:  List of users. 

---

<a href="https://github.com/ml-tooling/contaxy/blob/main/backend/src/contaxy/operations/user.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update_user`

```python
update_user(user_id: str, user_input: UserInput) → User
```

Updates the user metadata. 

This will update only the properties that are explicitly set in the `user_input`. The patching is based on the JSON Merge Patch Standard [RFC7396](https://tools.ietf.org/html/rfc7396). 



**Args:**
 
 - <b>`user_id`</b> (str):  The ID of the user. 
 - <b>`user_input`</b> (UserInput):  The user data used to update the user. 



**Raises:**
 
 - <b>`ResourceNotFoundError`</b>:  If no user with the specified ID exists. 



**Returns:**
 
 - <b>`User`</b>:  The updated user information. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
