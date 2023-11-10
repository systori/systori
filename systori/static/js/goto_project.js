/**
 * Class representing a navigation element to jump to a project by project id.
 * @extends HTMLElement
 * @property {HTMLSpanElement} infoBox
 * @property {number} queryPk
 * @property {boolean} projectFouund
 */
class SystoriGotoProject extends HTMLElement {
    infoBox;
    queryPk;
    projectFound;
    /**
     * Create a SystoriGotoProject Element.
     */
    constructor() {
        super();
        this.infoBox = document.querySelector("#infoBox");
        this.queryPk = 0;
        this.projectFound = false;

        this.addEventListener('keyup', e => {
            this.handleKeyup(e);
        });
        this.addEventListener('keydown', e => {
            this.handleKeydown(e);
        });
    }

    /**
     * showInfo method
     * @param {any} response - Info message to be displayed in UI
     * @param {string} type - Info message type
     */
    showInfo(response, type) {
        this.infoBox.className = "input-group-addon";
        if (type == "success") {
            this.infoBox.classList.add("label-success");
            this.infoBox.innerText = `${response.name}`;
        } else if (type == "warning") {
            this.infoBox.classList.add("label-warning");
            this.infoBox.innerText = `${response.name}`;
        } else if (type == "reset") {
            this.infoBox.innerText = '#';
        }
    }

    async fetchProject() {
        let response = await fetch(
            `${window.location.origin}/api/project/${this.queryPk}/exists/`,
            { credentials: 'include' }
        );
        if (response.status == 200) {
            this.showInfo(await response.json(), "success");
            this.projectFound = true;
        } else if (response.status == 206) {
            this.showInfo(await response.json(), "warning");
            this.projectFound = false;
        }
    }

    /**
     * showInfo method
     * @param {KeyboardEvent} event
     */
    async handleKeyup(event) {
        this.queryPk = parseInt((/** @type {HTMLElement} */ event.target).innerText)
        if (isNaN(this.queryPk)) {
            this.showInfo("", "reset");
        } else {
            await this.fetchProject();
        }
    }

    /**
     * showInfo method
     * @param {KeyboardEvent} event
     */
    handleKeydown(event) {
        if (event.key == "Enter" && this.projectFound == true) {
            event.preventDefault();
            window.location.href = `${window.location.origin}/project-${this.queryPk}`;
        } else if (event.key == "Enter") {
            event.preventDefault();
        }
    }
}

window.customElements.define("sys-goto-project", SystoriGotoProject);