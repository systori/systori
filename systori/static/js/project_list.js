/**
 * Retrieves a cookie value by name
 * @param {string} query - The name of the cookie
 * @returns {string} - The value of the cookie
 */
function getCookie(query) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const [name, value] = cookies[i].trim().split('=');
        if (name === query) {
            return value;
        }
    }
    return '';
}

const filterBar = document.querySelector('.filter-bar');
const tileContainer = document.querySelector('.tile-container');
const csrfToken = getCookie('csrftoken');
const headers = new Headers({
    'Content-Type': 'application/json',
    Accept: 'application/json',
    'X-CSRFToken': csrfToken,
});

/**
 * Enum for project phase order.
 * @enum {number}
 */
const PhaseOrder = {
    prospective: 0,
    tendering: 1,
    planning: 2,
    executing: 3,
    settlement: 4,
    warranty: 5,
    finished: 6,
};

/**
 * Enum for sort button types.
 * @enum {string}
 */
const SortButtonType = {
    id: 'id',
    name: 'name',
    phase: 'phase',
};

/**
 * SystoriProjectTile custom element that extends HTMLElement.
 */
class SystoriProjectTile extends HTMLElement {
    constructor() {
        super();
    }

    /**
     * Gets the primary key of the project.
     * @return {number} The parsed integer from the data-pk attribute.
     */
    get pk() {
        return parseInt(this.dataset.pk);
    }

    /**
     * Gets the name of the project.
     * @return {string} The value of the data-name attribute.
     */
    get name() {
        return this.dataset.name;
    }

    /**
     * Gets the phase of the project. Defaults to PhaseOrder.prospective if not set.
     * @return {number|string} The phase of the project.
     */
    get phase() {
        return this.dataset.phase || PhaseOrder.prospective;
    }

    /**
     * Determines if the tile is hidden.
     * @return {boolean} True if the tile has 'hidden' class, false otherwise.
     */
    get hidden() {
        return this.classList.contains('hidden');
    }

    /**
     * Hides or shows the project tile based on the argument.
     * @param {boolean} hide - If true, hides the tile, otherwise shows it.
     */
    hide(hide) {
        hide ? this.classList.add('hidden') : this.classList.remove('hidden');
    }
}

/**
 * SystoriSortButton custom element that extends HTMLElement for sorting project tiles.
 */
class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    /**
     * Gets the sorting type from the data-type attribute.
     * @return {string} The sorting type.
     */
    get type() {
        return this.dataset.type;
    }
    /**
     * Sets the sorting type in the data-type attribute.
     * @param {string} type - The type of sorting to be set.
     */
    set type(type) {
        this.dataset.type = type;
    }
    /**
     * Gets the ascending sort order status from the data-asc attribute.
     * @return {boolean} True if sorting should be in ascending order, false otherwise.
     */
    get asc() {
        return this.dataset.asc === "true";
    }
    /**
     * Sets the ascending sort order status in the data-asc attribute.
     * @param {boolean} asc - The ascending order status to be set.
     */
    set asc(asc) {
        console.log("updating asc");
        asc ? (this.dataset.asc = "true") : (this.dataset.asc = "false");
    }
    toggleAsc() {
        this.asc = !this.asc;
    }
    /**
     * Gets the active status of the sort button.
     * @return {boolean} True if the sort button is active, false otherwise.
     */
    get active() {
        return this.classList.contains('active');
    }
    /**
     * Sets the active status of the sort button.
     * @param {boolean} status - If true, sets the sort button to active, otherwise inactive.
     */
    set active(status) {
        this.classList.toggle('active', status);
    }

    clickHandler() {
        this.toggleAsc();
        this.activateExclusive();
        this.sortProjectTiles();
        this._saveStateToLocalStorage();
    }

    // adds class `active` to active button and removes it from all others.
    activateExclusive() {
        const btns = Array.from(
            document.querySelectorAll("sys-sort-button"),
        );
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
    }

    sortProjectTiles() {
        const projectTiles = Array.from(
            document.querySelectorAll(".tile"),
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
                        return a.dataset.name.localeCompare(b.dataset.name);
                    } else {
                        return b.dataset.name.localeCompare(a.dataset.name);
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
    /**
     * Saves the current state to local storage.
     * @private
     */
    _saveStateToLocalStorage() {
        localStorage.setItem(
            "state-SystoriSortButton",
            JSON.stringify({
                type: this.type,
                asc: this.asc,
            }),
        );
    }
    /**
     * Loads the state from local storage.
     * @private
     */
    _loadStateFromLocalStorage() {
        const state = JSON.parse(
            localStorage.getItem("state-SystoriSortButton")
        );
        if (state) {
            if (this.type === state.type) {
                this.asc = state.asc;
                this.active = true;
                this.sortProjectTiles();
            } else {
                // delete this.dataset.active;
                this.active = false;
            }
        }
    }
    connectedCallback() {
        this._loadStateFromLocalStorage();
    }
}
/**
 * SystoriPhaseButton custom element that extends HTMLElement for filtering project tiles based on phase.
 */
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    /**
     * Gets the phase associated with the button from the data-phase attribute.
     * @return {string} The phase value.
     */
    get phase() {
        return this.dataset.phase;
    }
    /**
     * Sets the phase in the data-phase attribute associated with the button.
     * @param {string} phase - The phase to be set.
     */
    set phase(phase) {
        this.dataset.phase = phase;
    }
    /**
     * Gets the hidden status of the phase.
     * @return {boolean} True if the phase is hidden, false otherwise.
     */
    get hidePhase() {
        return this.classList.contains("hide-phase");
    }
    /**
     * Sets the hidden status of the phase.
     * @param {boolean} hide - If true, hides the phase, otherwise shows it.
     */
    set hidePhase(hide) {
        hide
            ? this.classList.add("hide-phase")
            : this.classList.remove("hide-phase");
    }
    /**
     * Toggles the visibility of project tiles based on the phase.
     * @param {boolean} status - The visibility status to apply to the project tiles.
     */
    toggleProjectTiles(status) {
        const projectTiles = Array.from(
            document.querySelectorAll(
                `sys-project-tile[data-phase=${this.phase}]`,
            ),
        );
        for (const tile of projectTiles) {
            tile.hide(status);
        }
    }
    /**
     * Handles the click event on the phase button, toggles the visibility of the related project tiles,
     * shows a warning message if necessary, and saves the state to local storage.
     */
    clickHandler() {
        this.hidePhase = !this.hidePhase;
        this.filterProjectTiles();
        this.showWarningMessage();
        this._saveStateToLocalStorage();
    }
    /**
     * Filters the project tiles based on the current phase's hidden status.
     */
    filterProjectTiles() {
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
    /**
     * Displays a warning message if there are any hidden project tiles.
     */
    showWarningMessage() {
        let hiddenProjectTiles = document.querySelectorAll(".tile.hidden");
        let sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage) sysWarningMessage.warnFilteredProjects(hiddenProjectTiles.length || 0);
    }
    /**
     * Saves the current state of the phase button to local storage.
     * @private
     */
    _saveStateToLocalStorage() {
        localStorage.setItem(
            `state-SystoriPhaseButton-${this.phase}`,
            JSON.stringify({
                hidePhase: this.hidePhase,
            }),
        );
    }
    /**
     * Loads the state of the phase button from local storage.
     * @private
     */
    _loadStateFromLocalStorage() {
        const stateJson = localStorage.getItem(
            `state-SystoriPhaseButton-${this.phase}`,
        );
        if (stateJson) {
            const state = JSON.parse(stateJson);
            this.hidePhase = state.hidePhase;
            this.filterProjectTiles();
            this.showWarningMessage();
        }
    }
    connectedCallback() {
        this._loadStateFromLocalStorage();
    }
}

class SystoriSearchElement extends HTMLElement {
    // This custom element is for composing the two childNodes.
    constructor() {
        super();
    }
}
/**
 * SystoriSearchInput extends the HTMLInputElement and is responsible for 
 * handling search functionality and filtering of project tiles.
 */
class SystoriSearchInput extends HTMLInputElement {
    /**
     * Holds the timeout ID for the delayed search handler.
     */
    timeout;

    constructor() {
        super();
        this.addEventListener("keyup", () => this.clickHandler());
    }
    /**
     * Filters project tiles based on search results.
     * @param {number[]} searchResultPks - An array of project primary keys (pks) that are the search results.
     */
    filterProjectTiles(searchResultPks) {
        const projectPks = this.getAllLocalProjectPks();
        // all projects except the found projects
        const difference = projectPks.filter(
            pk => !searchResultPks.includes(pk),
        );
        for (const pk of difference) {
            const tile = document.querySelector(
                `sys-project-tile[data-pk="${pk}"]`,
            );
            if (tile) tile.hide(true);
        }

        const sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage) sysWarningMessage.warnFilteredProjects(difference.length);

    }
    /**
     * Shows all projects that are not currently filtered out by phase buttons.
     */
    showAllVisibleProjects() {
        const phaseBtns = new Map();
        Array.from(
            document.querySelectorAll("sys-phase-button"),
        ).map(tile => phaseBtns.set(tile.phase, tile.hidePhase));
        const projectPks = this.getAllLocalProjectPks();
        var countHiddenProjects = projectPks.length;
        for (const pk of projectPks) {
            const tile = document.querySelector(
                `sys-project-tile[data-pk="${pk}"]`,
            );
            if (tile && !phaseBtns.get(tile.phase)) {
                tile.hide(false);
                countHiddenProjects--;
            }
        }
        const cancelButton = document.querySelector(
            "sys-search-cancel-button",
        );
        cancelButton.visible = false;
        const sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage) sysWarningMessage.warnFilteredProjects(countHiddenProjects);
    }
    /**
     * Retrieves all project primary keys (pks) from the local tiles.
     * @return {number[]} An array of all local project pks.
     */
    getAllLocalProjectPks() {
        return Array.from(
            document.querySelectorAll(`sys-project-tile`),
        ).map(tile => {
            return tile.pk;
        });
    }
    /**
     * Performs a search query to the API and filters project tiles based on the search results.
     */
    apiSearchProjects() {
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
    /**
     * Processes the search query after user input.
     */
    processQuery() {
        const cancelButton = document.querySelector(
            "sys-search-cancel-button",
        );
        cancelButton.visible = true;
        this.apiSearchProjects();
    }
    /**
     * Delays the execution of the click handler to debounce user input.
     */
    delayedClickHandler() {
        this.value == "" ? this.showAllVisibleProjects() : this.processQuery();
    }
    /**
     * Handles the keyup event, setting a timeout to debounce the search functionality.
     */
    clickHandler() {
        if (this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.value == "" ? this.showAllVisibleProjects() : this.processQuery();
        }, 300);
    }
}
/**
 * SystoriSearchCancelButton extends HTMLElement to provide a custom button
 * that clears the search input and resets the visibility of project tiles.
 */
class SystoriSearchCancelButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    /**
     * Indicates whether the cancel button is visible.
     * @return {boolean} Visibility status of the cancel button.
     */
    get visible() {
        return this.classList.contains("visible");
    }
    /**
     * Sets the visibility of the cancel button.
     * @param {boolean} status - The desired visibility state.
     */
    set visible(status) {
        this.classList.toggle("visible", status);
    }
    /**
     * Handles the click event for the cancel button, clearing the associated search input
     * and hiding itself.
     */
    clickHandler() {
        if (this.parentElement) {
            const input = this.parentElement.querySelector(
                'input[is="sys-search-input"]',
            );
            if (input) {
                input.value = "";
                input.showAllVisibleProjects();
                this.visible = false;
            }
        }
    }
}
/**
 * SystoriWarningMessage extends HTMLElement to provide a custom element
 * that displays a warning message about the number of filtered projects.
 */
class SystoriWarningMessage extends HTMLElement {

    constructor() {
        super();
    }
    /**
     * Updates the warning message based on the number of filtered projects.
     * @param {number} count - The number of projects that are filtered and not currently displayed.
     */
    warnFilteredProjects(count) {
        let regex = /\$phaseFilteredProjects/gi;
        if (count > 0) {
            this.innerText = document.querySelector("#sys-phaseFilteredProjects-translated").innerText.replace(regex, count.toString());
            this.classList.remove("hidden");
        } else {
            this.classList.add("hidden");
        }
    }
    /**
     * Indicates whether the warning message is hidden.
     * @return {boolean} Visibility status of the warning message.
     */
    get hideWarningMessage() {
        return this.classList.contains('hidden');
    }
    /**
     * Sets the visibility of the warning message.
     * @param {boolean} hide - The desired visibility state.
     */
    set hideWarningMessage(hide) {
        hide
            ? this.classList.add('hidden')
            : this.classList.remove('hidden');
    }
}

customElements.define("sys-warning-message", SystoriWarningMessage);
customElements.define("sys-project-tile", SystoriProjectTile);
customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-search-cancel-button", SystoriSearchCancelButton);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);


if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}