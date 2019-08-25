const filterBar = document.querySelector("#filter-bar");
const tileContainer = document.querySelector("#tile-container");
enum PhaseOrder {
    prospective,
    tendering,
    planning,
    executing,
    settlement,
    warranty,
    finished,
}
enum SortButtonType {
    id = "id",
    name = "name",
    phase = "phase",
}

type SortButtonState = {
    type: string;
    asc: boolean;
};
type PhaseButtonState = {
    phase: string;
    hidePhase: boolean;
};

class SystoriProjectTile extends HTMLElement {
    constructor() {
        super();
    }
    get pk(): number {
        return parseInt(this.dataset["pk"]!);
    }
    get name(): string {
        return this.dataset["name"]!;
    }
    get phase(): PhaseOrder {
        return (this.dataset["phase"] || PhaseOrder.prospective) as PhaseOrder;
    }

    get hidden(): boolean {
        return this.classList.contains("hidden") === true;
    }
    hide(hide: boolean): void {
        hide ? this.classList.add("hidden") : this.classList.remove("hidden");
    }
}

class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.sortProjectTiles(true));
    }
    get type(): SortButtonType {
        switch (this.dataset["type"]) {
            case "id":
                return SortButtonType.id;
            case "name":
                return SortButtonType.name;
            case "phase":
                return SortButtonType.phase;
            default:
                throw Error("Couldn't catch SortButtonType.");
        }
    }
    set type(type: SortButtonType) {
        this.dataset["type"] = SortButtonType[type];
    }

    // ASC/DESC sorting order
    get asc(): boolean {
        return this.dataset["asc"] == "true";
    }
    set asc(asc: boolean) {
        asc ? (this.dataset["asc"] = "true") : (this.dataset["asc"] = "false");
    }
    toggleAsc(): void {
        this.asc = !this.asc;
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(status: boolean) {
        status ? this.classList.add("active") : this.classList.remove("active");
    }

    // adds class `active` to active button and removes it from all others.
    activateExclusive(): void {
        const btns: SystoriSortButton[] = Array.from(
            document.querySelectorAll("sys-sort-button"),
        );
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
    }

    sortProjectTiles(toggleAsc: boolean): void {
        // starting with toggling sorting order, move to bottom to exchange true/false behaviour
        if (toggleAsc) this.toggleAsc();
        this.activateExclusive();

        const projectTiles = Array.from(
            document.querySelectorAll<SystoriProjectTile>(".tile"),
        );

        projectTiles.sort((a, b) => {
            switch (this.type) {
                case SortButtonType.id:
                    if (this.asc) {
                        return b.pk < a.pk ? -1 : 1;
                    } else {
                        return a.pk < b.pk ? -1 : 1;
                    }
                case SortButtonType.name:
                    if (this.asc) {
                        return a.name.localeCompare(b.name);
                    } else {
                        return b.name.localeCompare(a.name);
                    }
                case SortButtonType.phase:
                    if (this.asc) {
                        return PhaseOrder[b.phase] <= PhaseOrder[a.phase]
                            ? -1
                            : 1;
                    } else {
                        return PhaseOrder[a.phase] <= PhaseOrder[b.phase]
                            ? -1
                            : 1;
                    }
                default:
                    throw new Error(
                        `Can't find a SortButtonType type for ${this.type}.`,
                    );
            }
        });

        if (tileContainer) {
            tileContainer.innerHTML = "";
            for (const tile of projectTiles) {
                tileContainer.appendChild(tile);
            }
        }

        this.saveStateToLocalStorage();
    }

    saveStateToLocalStorage(): void {
        localStorage.setItem(
            "state-SystoriSortButton",
            JSON.stringify({
                type: this.type,
                asc: this.asc,
            }),
        );
    }
}

function savePhaseStateToLocalStorage(): void {
    const btns: SystoriPhaseButton[] = Array.from(
        document.querySelectorAll("sys-phase-button"),
    );
    const btnsState: PhaseButtonState[] = [];
    for (const btn of btns) {
        btnsState.push({ phase: btn.phase, hidePhase: btn.hidePhase });
    }
    localStorage.setItem("state-SystoriPhaseButton", JSON.stringify(btnsState));
}

class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.filterProjectTiles(true));
    }

    get phase(): string {
        return this.dataset["phase"]!;
    }
    set phase(phase: string) {
        this.dataset["phase"] = phase;
    }

    // hidePhase === hidden
    get hidePhase(): boolean {
        return this.classList.contains("hide-phase");
    }
    set hidePhase(hide: boolean) {
        hide
            ? this.classList.add("hide-phase")
            : this.classList.remove("hide-phase");
    }

    toggleProjectTiles(hide: boolean): void {
        const projectTiles: SystoriProjectTile[] = Array.from(
            document.querySelectorAll(
                `sys-project-tile[data-phase=${this.phase}]`,
            ),
        );
        for (const tile of projectTiles) {
            tile.hide(hide);
        }
        savePhaseStateToLocalStorage();
    }

    filterProjectTiles(toggle: boolean): void {
        if (toggle) this.hidePhase = !this.hidePhase;
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
}

class SystoriSearchElement extends HTMLElement {
    // This custom element is for composing the two childNodes.
    constructor() {
        super();
    }
}

class SystoriSearchInput extends HTMLInputElement {
    constructor() {
        super();
        this.addEventListener("keyup", () => this.apiSearchProjects());
    }

    apiSearchProjects(): number[] {
        const projects = [] as number[];
        projects.push(11);
        projects.push(23);
        return projects;
    }
}

function loadLocalStorage(): void {
    const sortJson = localStorage.getItem("state-SystoriSortButton");
    const phaseJson = localStorage.getItem("state-SystoriPhaseButton");
    if (sortJson) {
        const state: SortButtonState = JSON.parse(sortJson);
        const btns: SystoriSortButton[] = Array.from(
            document.querySelectorAll("sys-sort-button"),
        );
        for (const btn of btns) {
            if (btn.type === state.type) {
                console.log(`loading from localStorage for ${btn.type}.`);
                btn.asc = state.asc;
                btn.sortProjectTiles(false);
            } else {
                btn.active = false;
            }
        }
    }
    if (phaseJson) {
        const state: PhaseButtonState[] = JSON.parse(phaseJson);
        const btns: SystoriPhaseButton[] = Array.from(
            document.querySelectorAll("sys-phase-button"),
        );
        for (const p of state) {
            if (p.hidePhase) {
                for (const btn of btns) {
                    if (btn.phase === p.phase) {
                        btn.hidePhase = p.hidePhase;
                        btn.filterProjectTiles(false);
                    }
                }
            }
        }
    }
}

customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);

loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}
