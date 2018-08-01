const infoBox = document.querySelector("#infoBox") as HTMLSpanElement;
let queryPk: number = 0;
let projectFound: boolean = false;

class SystoriGotoProject extends HTMLElement {
    
    constructor() {
        super();
        this.addEventListener('keyup', e => {
            this.handleKeyup(e);
        });
        this.addEventListener('keydown', e => {
            this.handleKeydown(e);
        });
    }

    showInfo(response: any, type: string) {
        infoBox.className = "input-group-addon";
        if (type == "success") {
            infoBox.classList.add("label-success");
            infoBox.innerText = `${response.name}`;
        } else if (type == "warning") {
            infoBox.classList.add("label-warning");
            infoBox.innerText = `${response.name}`;
        } else if (type == "reset") {
            infoBox.innerText = '#';
        }
    }

    async fetchProject(queryPk: number) {
        let response = await fetch(`${window.location.origin}/api/v1/projects/${queryPk}/exists/`);
        if (response.status == 200) {
            this.showInfo(await response.json(), "success");
            projectFound = true;
        } else if (response.status == 206) {
            this.showInfo(await response.json(), "warning");
            projectFound = false;
        }
    }

    async handleKeyup(event:KeyboardEvent) {
        queryPk = parseInt((event.target as HTMLElement).innerText)
        if (isNaN(queryPk)) {
            this.showInfo("", "reset");
        } else {
            await this.fetchProject(queryPk);
        }
    }
    handleKeydown(event: KeyboardEvent) {
        if (event.key == "Enter" && projectFound == true) {
            event.preventDefault();
            window.location.href = `${window.location.origin}/project-${queryPk}`;
        } else if (event.key == "Enter") {
            event.preventDefault();
        }
    }
}

window.customElements.define("sys-goto-project", SystoriGotoProject);