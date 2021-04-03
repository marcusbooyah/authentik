import * as Sentry from "@sentry/browser";
import { Integrations } from "@sentry/tracing";
import { VERSION } from "../constants";
import { SentryIgnoredError } from "../common/errors";
import { Config, Configuration, Middleware, ResponseContext, RootApi } from "authentik-api";
import { getCookie } from "../utils";
import { API_DRAWER_MIDDLEWARE } from "../elements/notifications/APIDrawer";
import { MessageMiddleware } from "../elements/messages/Middleware";

export class LoggingMiddleware implements Middleware {

    post(context: ResponseContext): Promise<Response | void> {
        console.debug(`authentik/api: ${context.init.method} ${context.url} => ${context.response.status}`);
        return Promise.resolve(context.response);
    }
}

export const DEFAULT_CONFIG = new Configuration({
    basePath: "/api/v2beta",
    headers: {
        "X-CSRFToken": getCookie("authentik_csrf"),
        "X-Authentik-Prevent-Basic": "true"
    },
    middleware: [
        API_DRAWER_MIDDLEWARE,
        new MessageMiddleware(),
        new LoggingMiddleware(),
    ],
});

export function configureSentry(): Promise<Config> {
    return new RootApi(DEFAULT_CONFIG).rootConfigList().then((config) => {
        if (config.errorReportingEnabled) {
            Sentry.init({
                dsn: "https://a579bb09306d4f8b8d8847c052d3a1d3@sentry.beryju.org/8",
                release: `authentik@${VERSION}`,
                integrations: [
                    new Integrations.BrowserTracing(),
                ],
                tracesSampleRate: 0.6,
                environment: config.errorReportingEnvironment,
                beforeSend(event: Sentry.Event, hint: Sentry.EventHint) {
                    if (hint.originalException instanceof SentryIgnoredError) {
                        return null;
                    }
                    return event;
                },
            });
            console.debug("authentik/config: Sentry enabled.");
        }
        return config;
    });
}
