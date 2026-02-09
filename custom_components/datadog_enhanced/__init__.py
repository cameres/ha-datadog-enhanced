"""Support for sending data to Datadog with enhanced tagging."""

import logging

from datadog import DogStatsd, initialize

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_PREFIX,
    EVENT_LOGBOOK_ENTRY,
    EVENT_STATE_CHANGED,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, state as state_helper

from . import config_flow as config_flow
from .const import CONF_RATE, DOMAIN

_LOGGER = logging.getLogger(__name__)

type DatadogEnhancedConfigEntry = ConfigEntry[DogStatsd]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)


def get_device_class_from_state(state) -> str | None:
    """Get device_class from a state object's attributes.

    Args:
        state: Home Assistant state object

    Returns:
        The device_class value if present, None otherwise.

    Examples:
        state.attributes = {"device_class": "temperature"} -> "temperature"
        state.attributes = {"device_class": "battery"} -> "battery"
        state.attributes = {} -> None
    """
    if state and hasattr(state, "attributes"):
        return state.attributes.get("device_class")
    return None


async def async_setup_entry(hass: HomeAssistant, entry: DatadogEnhancedConfigEntry) -> bool:
    """Set up Datadog Enhanced from a config entry."""

    data = entry.data
    options = entry.options
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    prefix = options[CONF_PREFIX]
    sample_rate = options[CONF_RATE]

    statsd_client = DogStatsd(
        host=host, port=port, namespace=prefix, disable_telemetry=True
    )
    entry.runtime_data = statsd_client

    initialize(statsd_host=host, statsd_port=port)

    def logbook_entry_listener(event):
        name = event.data.get("name")
        message = event.data.get("message")
        entity_id = event.data.get("entity_id")

        tags = [
            f"entity:{entity_id}",
            f"domain:{event.data.get('domain')}",
        ]

        # Add entity_type tag from device_class if available
        if entity_id:
            state = hass.states.get(entity_id)
            if device_class := get_device_class_from_state(state):
                tags.append(f"entity_type:{device_class}")

        entry.runtime_data.event(
            title="Home Assistant",
            message=f"%%% \n **{name}** {message} \n %%%",
            tags=tags,
        )

    def state_changed_listener(event):
        state = event.data.get("new_state")
        if state is None or state.state == STATE_UNKNOWN:
            return

        metric = f"{prefix}.{state.domain}"
        tags = [f"entity:{state.entity_id}"]

        # Add entity_type tag from device_class if present in attributes
        if device_class := get_device_class_from_state(state):
            tags.append(f"entity_type:{device_class}")

        for key, value in state.attributes.items():
            if isinstance(value, (float, int, bool)):
                value = int(value) if isinstance(value, bool) else value
                attribute = f"{metric}.{key.replace(' ', '_')}"
                entry.runtime_data.gauge(
                    attribute, value, sample_rate=sample_rate, tags=tags
                )

        try:
            value = state_helper.state_as_number(state)
            entry.runtime_data.gauge(metric, value, sample_rate=sample_rate, tags=tags)
        except ValueError:
            pass

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_LOGBOOK_ENTRY, logbook_entry_listener)
    )
    entry.async_on_unload(
        hass.bus.async_listen(EVENT_STATE_CHANGED, state_changed_listener)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: DatadogEnhancedConfigEntry) -> bool:
    """Unload a Datadog Enhanced config entry."""
    runtime = entry.runtime_data
    runtime.flush()
    runtime.close_socket()
    return True
