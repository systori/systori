function getCookie(query: string): string {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const [name, value] = cookie.split("=");
        if (name === query) {
            return value;
        }
    }
    return "";
}
const filterBar = document.querySelector(".filter-bar");
const tileContainer = document.querySelector(".tile-container");
const csrfToken = getCookie("csrftoken");
const headers = new Headers({
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-CSRFToken": csrfToken,
});
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
    timeout: ReturnType<typeof setTimeout> | undefined;

    constructor() {
        super();
        this.addEventListener("keyup", () => this.clickHandler());
    }

    filterProjectTiles(searchResultPks: number[]): void {
        const projectPks = this.getAllLocalProjectPks();
        // all projects except the found projects
        const difference = projectPks.filter(
            pk => !searchResultPks.includes(pk),
        );
        for (const pk of difference) {
            const tile = document.querySelector<SystoriProjectTile>(
                `sys-project-tile[data-pk="${pk}"]`,
            );
            if (tile) tile.hide(true);
        }
    }

    showAllProjects(): void {
        const phaseBtns = new Map();
        Array.from(
            document.querySelectorAll<SystoriPhaseButton>("sys-phase-button"),
        ).map(tile => phaseBtns.set(tile.phase, tile.hidePhase));
        const projectPks = this.getAllLocalProjectPks();
        for (const pk of projectPks) {
            const tile = document.querySelector<SystoriProjectTile>(
                `sys-project-tile[data-pk="${pk}"]`,
            );
            if (tile && !phaseBtns.get(tile.phase)) tile.hide(false);
        }
        const cancelButton = document.querySelector<SystoriSearchCancelButton>(
            "sys-search-cancel-button",
        )!;
        cancelButton.visible = false;
    }

    getAllLocalProjectPks(): number[] {
        return Array.from(
            document.querySelectorAll<SystoriProjectTile>(`sys-project-tile`),
        ).map(tile => {
            return tile.pk;
        });
    }

    apiSearchProjects(): void {
        localStorage.setItem("sys-project-search-input", this.value);
        fetch("/api/project/search/", {
            method: "put",
            credentials: "same-origin",
            headers: headers,
            body: JSON.stringify({ query: this.value }),
        })
            .then(response => response.json())
            .then(body => {
                this.filterProjectTiles(body.projects);
            });
    }

    processQuery(): void {
        const cancelButton = document.querySelector<SystoriSearchCancelButton>(
            "sys-search-cancel-button",
        )!;
        cancelButton.visible = true;
        this.apiSearchProjects();
    }

    delayedClickHandler(): void {
        this.value == "" ? this.showAllProjects() : this.processQuery();
    }

    clickHandler(): void {
        if (this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.value == "" ? this.showAllProjects() : this.processQuery();
        }, 300);
    }
}

class SystoriSearchCancelButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    get visible(): boolean {
        return this.classList.contains("visible");
    }
    set visible(status: boolean) {
        this.classList.toggle("visible", status);
    }
    clickHandler(): void {
        if (this.parentElement) {
            const input = this.parentElement.querySelector<SystoriSearchInput>(
                'input[is="sys-search-input"]',
            );
            if (input) {
                input.value = "";
                input.showAllProjects();
                this.visible = false;
            }
        }
    }
}

customElements.define("sys-project-tile", SystoriProjectTile);
customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-search-cancel-button", SystoriSearchCancelButton);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);

// loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}
