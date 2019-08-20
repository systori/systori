"use strict";
let searchRequestFired = false;
let attemptMade = false;
let searchMatches;
let phaseFilter;
let phaseOrder = [
    "prospective",
    "tendering",
    "planning",
    "executing",
    "settlement",
    "warranty",
    "finished"
];
function sortProjects(e) {
    if (e == null)
        return;
    let lookup = new Map();
    let multimap = new Map();
    let i = 0;
    let btn = e.target;
    btn.activateExclusive();
    if (btn.type == "id") {
        console.log("id");
    }
    else if (btn.type == "name") {
        console.log("name");
    }
    else if (btn.type == "phase") {
        console.log("phase");
    }
}
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-phase-button";
    }
    get phase() {
        return this.dataset["phase"] || "";
    }
    set phase(phase) {
        this.dataset["phase"] = phase;
    }
    get hidePhase() {
        return this.dataset["hide-phase"] == "true";
    }
    get visiblePhase() {
        return !this.hidePhase;
    }
    set hidePhase(hidePhase) {
        hidePhase
            ? this.dataset["hide-phase"] = "true"
            : this.dataset["hide-phase"] = "false";
    }
    hide() {
        this.hidePhase = true;
        phaseFilter = phaseFilter.filter(item => item != this.phase);
        this.classList.add("line_through");
    }
    show() {
        this.hidePhase = false;
        phaseFilter.push(this.phase);
        this.classList.remove("line_through");
    }
    updatePhaseFilter(e) {
        (phaseFilter.indexOf(this.phase) > -1)
            ? this.hide()
            : this.show();
    }
    connectedCallback() {
        if (this.dataset["phase"])
            this.phase = this.dataset["phase"];
        console.log("connected phase button");
    }
}
class SystoriSortButton extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-sort-button";
    }
    get type() {
        return this.dataset["type"] || "";
    }
    set type(type) {
        this.dataset["type"] = type;
    }
    get reversed() {
        return this.dataset["reversed"] == "true";
    }
    set reversed(reversed) {
        reversed ? this.dataset["reversed"] = "true" : this.dataset["reversed"] = "false";
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(active) {
        active ? this.classList.add("active") : this.classList.remove('active');
    }
    activateExclusive() {
        let btns = Array.from(this.parentElement.querySelectorAll("sys-sort-button"));
        for (let btn of btns) {
            btn.active = false;
        }
        this.active = true;
        localStorage["sys-sort-button"] = this.type;
        localStorage["sys-sort-button-reversed"] = this.reversed.toString();
    }
    connectedCallback() {
        if (this.dataset["type"] != null)
            this.type = this.dataset["type"];
        if (this.dataset["reversed"] != null)
            this.reversed = this.dataset["reversed"] == "true";
        console.log("connected sort button");
    }
}
class SystoriProjectTile extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-project-tile";
    }
    connectedCallback() {
        console.log("connected project tile");
    }
}
class SystoriWarningMessage extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-warning-message";
    }
    connectedCallback() {
        console.log("connected warning message");
    }
}
window.customElements.define("sys-phase-button", SystoriPhaseButton);
window.customElements.define("sys-sort-button", SystoriSortButton);
window.customElements.define("sys-project-tile", SystoriProjectTile);
window.customElements.define("sys-warning-message", SystoriWarningMessage);
//# sourceMappingURL=project_list.js.map