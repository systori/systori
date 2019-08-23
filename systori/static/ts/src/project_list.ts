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

class SystoriProjectTile extends HTMLElement {
    constructor() {
        super();
    }
    get pk(): number {
        return Number(this.dataset["pk"]!);
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
        this.addEventListener("click", () => this.sortProjectTiles());
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

    get reversed(): boolean {
        return this.dataset["reversed"] == "true";
    }
    set reversed(reversed: boolean) {
        reversed
            ? (this.dataset["reversed"] = "true")
            : (this.dataset["reversed"] = "false");
    }
    toggleReversed(): void {
        this.reversed = !this.reversed;
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(active: boolean) {
        active ? this.classList.add("active") : this.classList.remove("active");
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
        this.toggleReversed();
        this.activateExclusive();

        const projectTiles = Array.from(
            document.querySelectorAll<SystoriProjectTile>(".tile"),
        );

        projectTiles.sort((a, b) => {
            if (this.type === "id") {
                if (this.reversed) {
                    return b.pk < a.pk ? -1 : 1;
                } else {
                    return a.pk < b.pk ? -1 : 1;
                }
            } else if (this.type === "name") {
                if (this.reversed) {
                    return a.name.localeCompare(b.name);
                } else {
                    return b.name.localeCompare(a.name);
                }
            } else if (this.type === "phase") {
                if (this.reversed) {
                    return PhaseOrder[b.phase] <= PhaseOrder[a.phase] ? -1 : 1;
                } else {
                    return PhaseOrder[a.phase] <= PhaseOrder[b.phase] ? -1 : 1;
                }
            } else {
                throw new Error("Unkown Button type.");
            }
        });

        if (tileContainer) {
            tileContainer.innerHTML = "";
            for (const tile of projectTiles) {
                tileContainer.appendChild(tile);
            }
        }
    }
}

class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.filterProjectTiles());
    }

    get phase(): string {
        return this.dataset["phase"]!;
    }
    set phase(phase: string) {
        this.dataset["phase"] = phase;
    }

    get hidePhase(): boolean {
        return this.classList.contains("hide-phase");
    }
    set hidePhase(hide: boolean) {
        hide
            ? this.classList.add("hide-phase")
            : this.classList.remove("hide-phase");
    }

    toggleHidePhase(): void {
        this.hidePhase = !this.hidePhase;
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
    }

    filterProjectTiles(): void {
        this.toggleHidePhase();
        console.log(this.phase);
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
}

customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);

if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}
