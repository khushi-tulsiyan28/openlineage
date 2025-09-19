-- OpenAPI Specification Endpoint
local cjson = require "cjson"

local openapi_spec = {
    openapi = "3.0.0",
    info = {
        title = "MLOps API Gateway",
        version = "1.0.0",
        description = "API Gateway for MLOps services with OAuth 2.0 authentication"
    },
    servers = {
        {
            url = "http://localhost:8081",
            description = "Development server"
        }
    },
    paths = {
        ["/health"] = {
            get = {
                summary = "Health Check",
                description = "Check the health status of the API Gateway",
                responses = {
                    ["200"] = {
                        description = "Service is healthy",
                        content = {
                            ["application/json"] = {
                                schema = {
                                    type = "object",
                                    properties = {
                                        status = { type = "string", example = "healthy" },
                                        timestamp = { type = "string", format = "date-time" },
                                        service = { type = "string", example = "nginx-gateway" }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        ["/oauth/authorize"] = {
            get = {
                summary = "Get OAuth Authorization URL",
                description = "Get the Microsoft Entra ID authorization URL",
                responses = {
                    ["200"] = {
                        description = "Authorization URL",
                        content = {
                            ["application/json"] = {
                                schema = {
                                    type = "object",
                                    properties = {
                                        authorization_url = { type = "string", format = "uri" }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        ["/oauth/callback"] = {
            get = {
                summary = "OAuth Callback",
                description = "Handle OAuth callback from Microsoft Entra ID",
                parameters = {
                    {
                        name = "code",
                        in = "query",
                        required = true,
                        schema = { type = "string" },
                        description = "Authorization code from Microsoft"
                    }
                },
                responses = {
                    ["302"] = {
                        description = "Redirect to MLflow UI"
                    },
                    ["400"] = {
                        description = "Bad request - missing or invalid code"
                    }
                }
            }
        },
        ["/oauth/token"] = {
            post = {
                summary = "Exchange Authorization Code for Token",
                description = "Exchange authorization code for access token",
                parameters = {
                    {
                        name = "code",
                        in = "query",
                        required = true,
                        schema = { type = "string" },
                        description = "Authorization code"
                    },
                    {
                        name = "redirect_uri",
                        in = "query",
                        required = true,
                        schema = { type = "string" },
                        description = "Redirect URI used in authorization"
                    }
                },
                responses = {
                    ["200"] = {
                        description = "Token response",
                        content = {
                            ["application/json"] = {
                                schema = {
                                    type = "object",
                                    properties = {
                                        access_token = { type = "string" },
                                        token_type = { type = "string" },
                                        expires_in = { type = "integer" },
                                        refresh_token = { type = "string" },
                                        scope = { type = "string" }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        ["/mlflow/{path}"] = {
            get = {
                summary = "MLflow Proxy",
                description = "Proxy requests to MLflow service",
                security = { { bearerAuth = {} } },
                parameters = {
                    {
                        name = "path",
                        in = "path",
                        required = true,
                        schema = { type = "string" },
                        description = "MLflow API path"
                    }
                },
                responses = {
                    ["200"] = {
                        description = "MLflow response"
                    },
                    ["401"] = {
                        description = "Unauthorized - valid JWT token required"
                    }
                }
            }
        },
        ["/feast/{path}"] = {
            get = {
                summary = "Feast Proxy",
                description = "Proxy requests to Feast service",
                security = { { bearerAuth = {} } },
                parameters = {
                    {
                        name = "path",
                        in = "path",
                        required = true,
                        schema = { type = "string" },
                        description = "Feast API path"
                    }
                },
                responses = {
                    ["200"] = {
                        description = "Feast response"
                    },
                    ["401"] = {
                        description = "Unauthorized - valid JWT token required"
                    }
                }
            }
        }
    },
    securitySchemes = {
        bearerAuth = {
            type = "http",
            scheme = "bearer",
            bearerFormat = "JWT"
        }
    }
}

ngx.header.content_type = "application/json"
ngx.say(cjson.encode(openapi_spec))
