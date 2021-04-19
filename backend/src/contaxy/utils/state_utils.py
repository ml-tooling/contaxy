"""Utilities for managing global and request state for an FastAPI app."""

from typing import Any, Callable, Optional

import addict
from starlette import datastructures

from contaxy.config import Settings
from contaxy.schema import AuthorizedAccess


class _Dict(addict.Dict):
    def __missing__(self, key):  # type: ignore
        # Do not create empty dict objects (default)
        return None


class State:
    _SHARED_NAMESPACE_KEY = "shared"

    def __init__(self, state: datastructures.State):
        """Initializes the state."""
        # Add namespaces attribute to state
        if not hasattr(state, "namespaces"):
            state.namespaces = {}
        self._namespaces = state.namespaces

        # Add close callbacks attribute to state
        if not hasattr(state, "_close_callbacks"):
            state._close_callbacks = []
        self._close_callbacks = state._close_callbacks

    @property
    def namespaces(self) -> dict:
        return self._namespaces

    def __getitem__(self, namespace: Any) -> addict.Dict:
        if namespace not in self._namespaces:
            self._namespaces[namespace] = _Dict()
        return self._namespaces[namespace]

    def __setitem__(self, namespace: Any, value: Any) -> None:
        if namespace == State._SHARED_NAMESPACE_KEY:
            raise ValueError("The shared namespace is not allowed to be set.")
        self._namespaces[namespace] = value

    def __delitem__(self, namespace: Any) -> None:
        if namespace in self._namespaces:
            del self._namespaces[namespace]

    def __enter__(self) -> "State":
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self.close()

    @property
    def shared_namespace(self) -> addict.Dict:
        return self[State._SHARED_NAMESPACE_KEY]

    def register_close_callback(self, callback_func: Callable) -> None:
        """Registers a close callback.

        All registered callback functions are called when the state is closed.
        """
        self._close_callbacks.append(callback_func)

    def close(self) -> None:
        """Closes state.

        This will execute all registered close callback functions.
        This method is automatically called. Manual calls should only be done under careful consideration.
        """
        if self._close_callbacks:
            for close_callback in self._close_callbacks:
                close_callback()
        self._close_callbacks.clear()


class GlobalState(State):
    """Holds a global state of one app instance (process).

    The global state is created once for every app instance/process
    and can be used to store and share objects globally (between all components),
    such as DB connections, HTTP clients, or data caches.
    """

    _SETTINGS_KEY = "settings"

    def __init__(self, state: datastructures.State):
        """Initializes the global state.

        Args:
            state: The state object from the app (`app.state`)
        """
        super(GlobalState, self).__init__(state)

    @property
    def settings(self) -> Settings:
        """Returns the global platform settings."""
        return self.shared_namespace.settings

    @settings.setter
    def settings(self, settings: Settings) -> None:
        """Sets the global platform settings.

        This is automatically set at the start of the app instance/process.
        """
        self.shared_namespace.settings = settings


class RequestState(State):
    """Holds a state for a single request.

    The request state is created once for every request
    and can be used to store and share objects between all components,
    such as DB connections, HTTP clients, or data caches.
    """

    def __init__(self, state: datastructures.State):
        """Initializes the request state.

        Args:
            state: The state object from the request (`request.state`)
        """
        super(RequestState, self).__init__(state)

    @property
    def authorized_access(self) -> Optional[AuthorizedAccess]:
        """Returns the authorized access info for the request."""
        return self.shared_namespace.authorized_access

    @authorized_access.setter
    def authorized_access(self, authorized_access: AuthorizedAccess) -> None:
        """Sets the authorized access info."""
        self.shared_namespace.authorized_access = authorized_access

    @property
    def authorized_subject(self) -> str:
        """Convenience method to check for authorized_access being not None and returns the authorized_subject."""

        if self.authorized_access and self.authorized_access.authorized_subject:
            return self.authorized_access.authorized_subject
        else:
            return ""
