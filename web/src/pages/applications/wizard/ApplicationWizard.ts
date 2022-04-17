import { t } from "@lingui/macro";

import { customElement } from "@lit/reactive-element/decorators/custom-element.js";
import { CSSResult, LitElement, TemplateResult, html } from "lit";
import { property } from "lit/decorators.js";

import AKGlobal from "../../../authentik.css";
import PFButton from "@patternfly/patternfly/components/Button/button.css";
import PFRadio from "@patternfly/patternfly/components/Radio/radio.css";
import PFBase from "@patternfly/patternfly/patternfly-base.css";

import "./InitialApplicationWizardPage";
import "./TypeApplicationWizardPage";
import "./TypeProxyApplicationWizardPage";

@customElement("ak-application-wizard")
export class ApplicationWizard extends LitElement {
    static get styles(): CSSResult[] {
        return [PFBase, PFButton, AKGlobal, PFRadio];
    }

    @property({ type: Boolean })
    open = false;

    @property()
    createText = t`Create`;

    @property({ attribute: false })
    finalHandler: () => Promise<void> = () => {
        return Promise.resolve();
    };

    render(): TemplateResult {
        return html`
            <ak-wizard
                .open=${this.open}
                .steps=${["initial", "type"]}
                header=${t`New application`}
                description=${t`Create a new application.`}
                .finalHandler=${() => {
                    return this.finalHandler();
                }}
            >
                <ak-application-wizard-initial slot="initial"> </ak-application-wizard-initial>
                <ak-application-wizard-type slot="type"> </ak-application-wizard-type>
                <ak-application-wizard-type-proxy
                    slot="type-proxy"
                ></ak-application-wizard-type-proxy>
                <button slot="trigger" class="pf-c-button pf-m-primary">${this.createText}</button>
            </ak-wizard>
        `;
    }
}
