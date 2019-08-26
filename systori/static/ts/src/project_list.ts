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

interface SortButtonState {
    type: SortButtonType;
    asc: boolean;
}
interface PhaseButtonState {
    hidePhase: boolean;
}

class SystoriProjectTile extends HTMLElement {
    constructor() {
        super();
    }
    get pk(): number {
        return parseInt(this.dataset.pk!);
    }
    get name(): string {
        return this.dataset.name!;
    }
    get phase(): PhaseOrder {
        return (this.dataset.phase || PhaseOrder.prospective) as PhaseOrder;
    }
    get hidden(): boolean {
        return this.classList.contains("hidden");
    }
    hide(hide: boolean): void {
        hide ? this.classList.add("hidden") : this.classList.remove("hidden");
    }
}

class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    get type(): SortButtonType {
        switch (this.dataset.type) {
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
        this.dataset.type = SortButtonType[type];
    }

    // ASC/DESC sorting order
    get asc(): boolean {
        return this.dataset.asc == "true";
    }
    set asc(asc: boolean) {
        asc ? (this.dataset.asc = "true") : (this.dataset.asc = "false");
    }
    toggleAsc(): void {
        this.asc = !this.asc;
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(status: boolean) {
        this.classList.toggle("active", status);
    }

    clickHandler(): void {
        this.toggleAsc();
        this.activateExclusive();
        this.sortProjectTiles();
        this._saveStateToLocalStorage();
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

    sortProjectTiles(): void {
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
                    // ToDo: switch x.dataset.name! back to x.name if it works with _loadStateFromLocalStorage
                    if (this.asc) {
                        return a.dataset.name!.localeCompare(b.dataset.name!);
                    } else {
                        return b.dataset.name!.localeCompare(a.dataset.name!);
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

        this._saveStateToLocalStorage();
    }

    _saveStateToLocalStorage(): void {
        localStorage.setItem(
            "state-SystoriSortButton",
            JSON.stringify({
                type: this.type,
                asc: this.asc,
            }),
        );
    }
    _loadStateFromLocalStorage(): void {
        if (this.active || !this.active) {
            const sortJson = localStorage.getItem("state-SystoriSortButton");
            if (sortJson) {
                const state: SortButtonState = JSON.parse(sortJson);
                if (this.type === state.type) {
                    this.asc = state.asc;
                    this.active = true;
                    this.sortProjectTiles();
                } else {
                    delete this.dataset.active;
                    this.active = false;
                }
            }
        }
    }
    connectedCallback(): void {
        this._loadStateFromLocalStorage();
    }
}

class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }

    get phase(): string {
        return this.dataset.phase!;
    }
    set phase(phase: string) {
        this.dataset.phase = phase;
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
    toggleProjectTiles(status: boolean): void {
        const projectTiles: SystoriProjectTile[] = Array.from(
            document.querySelectorAll(
                `sys-project-tile[data-phase=${this.phase}]`,
            ),
        );
        for (const tile of projectTiles) {
            tile.hide(status);
        }
    }
    clickHandler(): void {
        this.hidePhase = !this.hidePhase;
        this.filterProjectTiles();
        this._saveStateToLocalStorage();
    }
    filterProjectTiles(): void {
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
    _saveStateToLocalStorage(): void {
        localStorage.setItem(
            `state-SystoriPhaseButton-${this.phase}`,
            JSON.stringify({
                hidePhase: this.hidePhase,
            }),
        );
    }
    _loadStateFromLocalStorage(): void {
        const stateJson = localStorage.getItem(
            `state-SystoriPhaseButton-${this.phase}`,
        );
        if (stateJson) {
            const state = JSON.parse(stateJson);
            this.hidePhase = state.hidePhase;
            this.filterProjectTiles();
        }
    }
    connectedCallback(): void {
        this._loadStateFromLocalStorage();
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

// function loadLocalStorage(): void {
//     // const sortJson = localStorage.getItem("state-SystoriSortButton");
//     const phaseJson = localStorage.getItem("state-SystoriPhaseButton");
//     // if (sortJson) {
//     //     const state: SortButtonState = JSON.parse(sortJson);
//     //     const btns: SystoriSortButton[] = Array.from(
//     //         document.querySelectorAll("sys-sort-button"),
//     //     );
//     //     for (const btn of btns) {
//     //         if (btn.type === state.type) {
//     //             btn.asc = state.asc;
//     //             btn.sortProjectTiles(false);
//     //         } else {
//     //             btn.active = false;
//     //         }
//     //     }
//     // }
//     if (phaseJson) {
//         const state: PhaseButtonState[] = JSON.parse(phaseJson);
//         const btns: SystoriPhaseButton[] = Array.from(
//             document.querySelectorAll("sys-phase-button"),
//         );
//         for (const p of state) {
//             if (p.hidePhase) {
//                 for (const btn of btns) {
//                     if (btn.phase === p.phase) {
//                         btn.hidePhase = p.hidePhase;
//                         btn.filterProjectTiles(false);
//                     }
//                 }
//             }
//         }
//     }
// }

customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);

// loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}
