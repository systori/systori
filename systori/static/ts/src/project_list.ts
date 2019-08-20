let searchRequestFired: boolean = false;
let attemptMade: boolean = false;
let searchMatches: Array<number>;
let phaseFilter: Array<string>;
let phaseOrder: Array<string> = [
    "prospective",
    "tendering",
    "planning",
    "executing",
    "settlement",
    "warranty",
    "finished"
];

function sortProjects(e: Event) {
    if (e == null) return;
    let lookup: Map<any, HTMLElement> = new Map();
    let multimap: Map<string, any> = new Map();
    let i: number = 0;

    let btn = e.target as SystoriSortButton;
    btn.activateExclusive()

    if (btn.type == "id") {
        Array.from(document.querySelectorAll<HTMLElement>(".tile"))
            .map(e => lookup.set(parseInt(e.dataset["pk"] || "0"), e))
    } else if (btn.type == "name") {
        Array.from(document.querySelectorAll<HTMLElement>(".tile"))
            .map(e => lookup.set(e.dataset["name"] || "", e))
    } else if (btn.type == "phase") {
        console.log("phase")
    }

    let sortedKeys: Array<number> = Array.from(lookup.keys()).sort();
    if (btn.reversed == true) {
        sortedKeys = sortedKeys.reverse();
        btn.reversed = false;
    } else if (btn.reversed == false) {
        btn.reversed = true;
    }

    let lastMoved: any = undefined;

    for (let key of sortedKeys) {
        if (lastMoved == undefined) {
            //lastMoved = lookup[key];
            continue;
        }
        //lastMoved.insertAdjacentElement("afterend", lookup[key]);
        //last_moved = lookup[key];
    }
}

class SystoriPhaseButton extends HTMLElement {
    tag: string = "sys-phase-button";

    get phase(): string {
        return this.dataset["phase"] || "";
    }
    set phase(phase: string) {
        this.dataset["phase"] = phase;
    }

    get hidePhase(): boolean {
        return this.dataset["hide-phase"] == "true";
    }
    get visiblePhase(): boolean {
        return !this.hidePhase;
    }
    set hidePhase(hidePhase: boolean) {
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

    updatePhaseFilter(e: Event) {
        (phaseFilter.indexOf(this.phase) > -1)
            ? this.hide()
            : this.show()
    }

    connectedCallback() {
        if (this.dataset["phase"]) this.phase = this.dataset["phase"] as string;
        console.log("connected phase button");
    }
}

class SystoriSortButton extends HTMLElement {
    tag: string = "sys-sort-button";

    get type(): string {
        return this.dataset["type"] || "";
    }
    set type(type: string) {
        this.dataset["type"] = type;
    }

    get reversed(): boolean {
        return this.dataset["reversed"] == "true";
    }
    set reversed(reversed: boolean) {
        reversed ? this.dataset["reversed"] = "true" : this.dataset["reversed"] = "false";
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(active: boolean) {
        active ? this.classList.add("active") : this.classList.remove('active');
    }

    activateExclusive() {
        let btns = Array.from(
            (this.parentElement as HTMLDivElement).querySelectorAll<SystoriSortButton>("sys-sort-button")
        );
        for (let btn of btns) {
            btn.active = false;
        }
        this.active = true;
        localStorage["sys-sort-button"] = this.type;
        localStorage["sys-sort-button-reversed"] = this.reversed.toString();
    }

    connectedCallback() {
        if (this.dataset["type"] != null) this.type = this.dataset["type"] as string;
        if (this.dataset["reversed"] != null) this.reversed = this.dataset["reversed"] == "true";
        console.log("connected sort button");
    }
}

class SystoriProjectTile extends HTMLElement {
    tag: string = "sys-project-tile";
    connectedCallback() {
        console.log("connected project tile");
    }
}

class SystoriWarningMessage extends HTMLElement {
    tag: string = "sys-warning-message";
    connectedCallback() {
        console.log("connected warning message");
    }
}


window.customElements.define("sys-phase-button", SystoriPhaseButton);
window.customElements.define("sys-sort-button", SystoriSortButton);
window.customElements.define("sys-project-tile", SystoriProjectTile);
window.customElements.define("sys-warning-message", SystoriWarningMessage);
