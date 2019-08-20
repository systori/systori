import { ArrayListMultimap } from "./lib/multimap";
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
    var lookup = new Map();
    let i = 0;
    let btn = e.target;
    btn.activateExclusive();
    if (btn.type == "id") {
        Array.from(document.querySelectorAll(".tile"))
            .map(e => lookup.set(parseInt(e.dataset["pk"] || "0"), e));
    }
    else if (btn.type == "name") {
        Array.from(document.querySelectorAll(".tile"))
            .map(e => lookup.set(e.dataset["name"] || "", e));
    }
    else if (btn.type == "phase") {
        let lookup2 = new ArrayListMultimap();
        lookup = new Map();
        Array.from(document.querySelectorAll(".tile"))
            .map(e => lookup2.put(e.dataset["phase"] || "", e));
        for (let key of phaseOrder) {
            // for (let element of lookup2[key]) {
            //     console.log(element);
            // }
            console.log(key);
        }
    }
    let sortedKeys = Array.from(lookup.keys()).ns.naturalSort();
    console.log(sortedKeys);
    if (btn.reversed == true) {
        sortedKeys = sortedKeys.reverse();
        btn.reversed = false;
    }
    else if (btn.reversed == false) {
        btn.reversed = true;
    }
    let lastMoved = undefined;
    for (let key of sortedKeys) {
        if (lastMoved == undefined) {
            //lastMoved = lookup[key];
            continue;
        }
        //lastMoved.insertAdjacentElement("afterend", lookup[key]);
        //last_moved = lookup[key];
    }
}
function updatePhaseFilter(e) {
    if (e == undefined)
        return;
    let btn = e.target;
    btn.updatePhaseFilter();
    localStorage["phaseFilter"] = JSON.stringify({ phaseFilter });
    filterProjects();
}
function filterProjects() {
    let warning = document.querySelector("sys-warning-message");
    warning.hideWarningMessage = true;
    let projects = document.querySelectorAll(".tile");
    for (let project of projects) {
        project.classList.add("hidden");
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
    updatePhaseFilter() {
        (phaseFilter.indexOf(this.phase) > -1)
            ? this.hide()
            : this.show();
    }
    connectedCallback() {
        if (this.dataset["phase"])
            this.phase = this.dataset["phase"];
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
        reversed
            ? this.dataset["reversed"] = "true"
            : this.dataset["reversed"] = "false";
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(active) {
        active
            ? this.classList.add("active")
            : this.classList.remove('active');
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
    }
}
class SystoriProjectTile extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-project-tile";
    }
    get hideProjectTile() {
        return this.classList.contains("hidden");
    }
    set hideProjectTile(hideProjectTile) {
        hideProjectTile
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}
class SystoriWarningMessage extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-warning-message";
    }
    warnPhaseFilteredProjects(phaseFilteredProjects) {
        if (phaseFilteredProjects > 0) {
            this.children[0].innerHTML =
                document.querySelector("#sys-phaseFilteredProjects-translated")
                    .innerText;
            this.classList.remove("hidden");
        }
    }
    get hideWarningMessage() {
        return this.classList.contains("hidden");
    }
    set hideWarningMessage(hideWarningMessage) {
        hideWarningMessage
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}
function loadLocalStorage() {
    document.querySelector("#filter-bar").classList.remove("hidden");
    document.querySelector("#tile-container").classList.remove("hidden");
}
window.customElements.define("sys-phase-button", SystoriPhaseButton);
window.customElements.define("sys-sort-button", SystoriSortButton);
window.customElements.define("sys-project-tile", SystoriProjectTile);
window.customElements.define("sys-warning-message", SystoriWarningMessage);
// add Event Listeners
for (let btn of document.querySelectorAll("sys-sort-button")) {
    btn.addEventListener("click", sortProjects);
}
for (let btn of document.querySelectorAll("sys-phase-button")) {
    btn.addEventListener("click", updatePhaseFilter);
}
// Load user (browser) data
loadLocalStorage();
