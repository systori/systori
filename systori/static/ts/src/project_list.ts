import { ArrayListMultimap, Multimap } from "@systori/lib/multimap";
import naturalSort from "natural-sort";

// const searchRequestFired = false;
// const attemptMade = false;
// let searchMatches: Array<number>;
let phaseFilter: Array<string>;
enum PhaseOrder {
    prospective = "prospective",
    tendering = "tendering",
    planning = "planning",
    executing = "executing",
    settlement = "settlement",
    warranty = "warranty",
    finished = "finished",
}

function sortProjects(e: Event): void {
    if (e == null) return;
    let lookup: Map<string | number, SystoriProjectTile> = new Map();
    // const i = 0;

    const btn = e.target as SystoriSortButton;
    btn.activateExclusive();

    if (btn.type == "id") {
        Array.from(document.querySelectorAll<SystoriProjectTile>(".tile")).map(
            e => lookup.set(parseInt(e.dataset["pk"] || "0"), e),
        );
    } else if (btn.type == "name") {
        Array.from(document.querySelectorAll<SystoriProjectTile>(".tile")).map(
            e => lookup.set(e.dataset["name"] || "", e),
        );
    } else if (btn.type == "phase") {
        const lookup2: Multimap<string, HTMLElement> = new ArrayListMultimap();
        lookup = new Map();
        Array.from(document.querySelectorAll<SystoriProjectTile>(".tile")).map(
            e => lookup2.put(e.dataset["phase"] || "", e),
        );
        for (const key in PhaseOrder) {
            // for (let element of lookup2[key]) {
            //     console.log(element);
            // }
            console.log(key);
        }
    }

    let sortedKeys: Array<string | number> = Array.from(lookup.keys()).sort(
        naturalSort(),
    );
    if (btn.reversed == true) {
        sortedKeys = sortedKeys.reverse();
        btn.reversed = false;
    } else if (btn.reversed == false) {
        btn.reversed = true;
    }

    let lastMoved = null;

    for (const key of sortedKeys) {
        if (lastMoved == null) {
            console.log(`lastMoved == ${lastMoved} with key == ${key}`);
            lastMoved = lookup.get(key);
            continue;
        }
        //lastMoved.insertAdjacentElement("afterend", lookup[key]);
        //last_moved = lookup[key];
    }
}

function filterProjects(): void {
    const warning = document.querySelector(
        "sys-warning-message",
    ) as SystoriWarningMessage;
    warning.hideWarningMessage = true;

    const projects = document.querySelectorAll<SystoriProjectTile>(".tile");
    for (const project of projects) {
        project.classList.add("hidden");
    }
}

function updatePhaseFilter(e: Event): void {
    if (e == undefined) return;
    const btn = e.target as SystoriPhaseButton;
    btn.updatePhaseFilter();
    localStorage["phaseFilter"] = JSON.stringify({ phaseFilter });
    filterProjects();
}

class SystoriPhaseButton extends HTMLElement {
    tag = "sys-phase-button";

    get phase(): string {
        return this.dataset["phase"] || "";
    }
    set phase(phase: string) {
        this.dataset["phase"] = phase;
    }

    get hidePhase(): boolean {
        return this.dataset["hide-phase"] == "true";
    }
    set hidePhase(hidePhase: boolean) {
        hidePhase
            ? (this.dataset["hide-phase"] = "true")
            : (this.dataset["hide-phase"] = "false");
    }
    get visiblePhase(): boolean {
        return !this.hidePhase;
    }

    hide(): void {
        this.hidePhase = true;
        phaseFilter = phaseFilter.filter(item => item != this.phase);
        this.classList.add("line_through");
    }

    show(): void {
        this.hidePhase = false;
        phaseFilter.push(this.phase);
        this.classList.remove("line_through");
    }

    updatePhaseFilter(): void {
        phaseFilter.includes(this.phase) ? this.hide() : this.show();
    }

    connectedCallback(): void {
        if (this.dataset["phase"]) this.phase = this.dataset["phase"] as string;
    }
}

class SystoriSortButton extends HTMLElement {
    tag = "sys-sort-button";

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
        reversed
            ? (this.dataset["reversed"] = "true")
            : (this.dataset["reversed"] = "false");
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(active: boolean) {
        active ? this.classList.add("active") : this.classList.remove("active");
    }

    activateExclusive(): void {
        const btns = Array.from(
            (this.parentElement as HTMLDivElement).querySelectorAll<
                SystoriSortButton
            >("sys-sort-button"),
        );
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
        localStorage["sys-sort-button"] = this.type;
        localStorage["sys-sort-button-reversed"] = this.reversed.toString();
    }

    connectedCallback(): void {
        if (this.dataset["type"] != null)
            this.type = this.dataset["type"] as string;
        if (this.dataset["reversed"] != null)
            this.reversed = this.dataset["reversed"] == "true";
    }
}

class SystoriProjectTile extends HTMLElement {
    tag = "sys-project-tile";

    get hideProjectTile(): boolean {
        return this.classList.contains("hidden");
    }
    set hideProjectTile(hideProjectTile: boolean) {
        hideProjectTile
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}

class SystoriWarningMessage extends HTMLElement {
    tag = "sys-warning-message";

    warnPhaseFilteredProjects(phaseFilteredProjects: number): void {
        if (phaseFilteredProjects > 0) {
            this.children[0].innerHTML = (document.querySelector(
                "#sys-phaseFilteredProjects-translated",
            ) as HTMLElement).innerText;
            this.classList.remove("hidden");
        }
    }

    get hideWarningMessage(): boolean {
        return this.classList.contains("hidden");
    }
    set hideWarningMessage(hideWarningMessage: boolean) {
        hideWarningMessage
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}

function loadLocalStorage(): void {
    (document.querySelector("#filter-bar") as HTMLElement).classList.remove(
        "hidden",
    );
    (document.querySelector("#tile-container") as HTMLElement).classList.remove(
        "hidden",
    );
}

window.customElements.define("sys-phase-button", SystoriPhaseButton);
window.customElements.define("sys-sort-button", SystoriSortButton);
window.customElements.define("sys-project-tile", SystoriProjectTile);
window.customElements.define("sys-warning-message", SystoriWarningMessage);

// add Event Listeners
for (const btn of document.querySelectorAll<SystoriSortButton>(
    "sys-sort-button",
)) {
    btn.addEventListener("click", sortProjects);
}

for (const btn of document.querySelectorAll<SystoriPhaseButton>(
    "sys-phase-button",
)) {
    btn.addEventListener("click", updatePhaseFilter);
}

// Load user (browser) data
loadLocalStorage();
