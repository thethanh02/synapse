#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright 2020-2021 The Matrix.org Foundation C.I.C.
# Copyright 2020 Quentin Gliech
# Copyright (C) 2023 New Vector, Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# See the GNU Affero General Public License for more details:
# <https://www.gnu.org/licenses/agpl-3.0.html>.
#
# Originally licensed under the Apache License, Version 2.0:
# <http://www.apache.org/licenses/LICENSE-2.0>.
#
# [This file includes modifications made by New Vector Limited]
#
#

from collections import Counter
from typing import Any, Collection, Iterable, List, Mapping, Optional, Tuple, Type

import attr

from synapse.config._util import validate_config
from synapse.config.sso import SsoAttributeRequirement
from synapse.types import JsonDict
from synapse.util.module_loader import load_module
from synapse.util.stringutils import parse_and_validate_mxc_uri

from ..util.check_dependencies import check_requirements
from ._base import Config, ConfigError, read_file


class LaoIDConfig(Config):
    section = "lao_id"

    def read_config(self, config: JsonDict, **kwargs: Any) -> None:
        self.lao_id_provider = _parse_lao_id_provider_config_dict(config.get("lao_id_provider"))
        if not self.lao_id_provider:
            return
        # TODO: validate config
        # check_requirements("lao_id")

    @property
    def lao_id_enabled(self) -> bool:
        # LaoID is enabled if we have a provider
        return bool(self.lao_id_provider)


# jsonschema definition of the configuration settings for an lao_id identity provider
LAO_ID_PROVIDER_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["client_id", "client_secret"],
    "properties": {
        "idp_name": {"type": "string"},
        "idp_icon": {"type": "string"},
        "idp_brand": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
            "pattern": "^[a-z][a-z0-9_.-]*$",
        },
        "issuer": {"type": "string"},
        "client_id": {"type": "string"},
        "client_secret": {"type": "string"},
        "authorization_endpoint": {"type": "string"},
        "token_endpoint": {"type": "string"},
    },
}

def _parse_lao_id_provider_config_dict(
    lao_id_config: JsonDict
) -> "LaoIDProviderConfig":
    """Take the configuration dict and parse it into an LaoIDProviderConfig

    Raises:
        ConfigError if the configuration is malformed.
    """

    return LaoIDProviderConfig(
        idp_name=lao_id_config.get("idp_name", "LAO_ID"),
        idp_icon=lao_id_config.get("idp_icon"),
        idp_brand=lao_id_config.get("idp_brand"),
        issuer=lao_id_config.get("issuer"),
        client_id=lao_id_config.get("client_id"),
        client_secret=lao_id_config.get("client_secret"),
        authorization_endpoint=lao_id_config.get("authorization_endpoint"),
        token_endpoint=lao_id_config.get("token_endpoint"),
    )


@attr.s(slots=True, frozen=True, auto_attribs=True)
class LaoIDProviderConfig:
    # user-facing name for this identity provider.
    idp_name: str

    # Optional MXC URI for icon for this IdP.
    idp_icon: Optional[str]

    # Optional brand identifier for this IdP.
    idp_brand: Optional[str]

    # the LAO_ID issuer. Used to validate tokens
    issuer: str

    # oauth2 client id to use
    client_id: str

    # oauth2 client secret to use. a secret.
    client_secret: str

    # the oauth2 authorization endpoint.
    authorization_endpoint: Optional[str]

    # the oauth2 token endpoint.
    token_endpoint: str
