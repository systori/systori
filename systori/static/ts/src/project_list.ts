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

class SystoriProjectTile extends HTMLDivElement {
    constructor() {
        super();
    }
    get pk(): number {
        return Number(this.dataset["pk"] || "0");
    }
    get name(): string {
        return this.dataset["name"] || "unknown";
    }
    get phase(): PhaseOrder {
        return (this.dataset["phase"] || PhaseOrder.prospective) as PhaseOrder;
    }
}

function sortProjectTiles(e: Event): void {
    const btn = e.target as SystoriSortButton;
    if (!btn)
        throw new Error(
            `Expected SystoriSortButton as EventTarget but got ${e.target}.`,
        );
    const projectTiles = Array.from(
        document.querySelectorAll<SystoriProjectTile>(".tile"),
    );

    if (btn.type === "id") {
        projectTiles.sort(function(
            a: SystoriProjectTile,
            b: SystoriProjectTile,
        ) {
            if (btn.reversed) {
                return b.pk - a.pk;
            } else {
                return a.pk - b.pk;
            }
        });
    } else if (btn.type === "name") {
        projectTiles.sort(function(
            a: SystoriProjectTile,
            b: SystoriProjectTile,
        ) {
            if (btn.reversed) {
                return a.name.localeCompare(b.name);
            } else {
                return b.name.localeCompare(a.name);
            }
        });
    } else if (btn.type === "phase") {
        projectTiles.sort(function(
            a: SystoriProjectTile,
            b: SystoriProjectTile,
        ) {
            if (btn.reversed) {
                return PhaseOrder[a.phase] - PhaseOrder[b.phase];
            } else {
                return PhaseOrder[a.phase] - PhaseOrder[b.phase];
            }
        });
    } else {
        throw new Error("Unkown Button type.");
    }

    if (tileContainer) {
        tileContainer.innerHTML = "";
        for (const tile of projectTiles) {
            tileContainer.appendChild(tile);
        }
    }
    console.log("sorting");
}

class SystoriSortButton extends HTMLButtonElement {
    constructor() {
        super();
        this.addEventListener("click", e => this.clickHandler(e));
    }
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
    toggleReversed(): void {
        this.reversed = !this.reversed;
    }

    get active(): boolean {
        return this.classList.contains("active");
    }
    set active(active: boolean) {
        active ? this.classList.add("active") : this.classList.remove("active");
    }
    clickHandler(e: Event): void {
        this.toggleReversed();
        sortProjectTiles(e);
    }
}

customElements.define("sys-sort-button", SystoriSortButton, {
    extends: "button",
});
customElements.define("sys-project-tile", SystoriProjectTile, {
    extends: "div",
});

if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}
