"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : new P(function (resolve) { resolve(result.value); }).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const infoBox = document.querySelector("#infoBox");
let queryPk = 0;
let projectFound = false;
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
    showInfo(response, type) {
        infoBox.className = "input-group-addon";
        if (type == "success") {
            infoBox.classList.add("label-success");
            infoBox.innerText = `${response.name}`;
        }
        else if (type == "warning") {
            infoBox.classList.add("label-warning");
            infoBox.innerText = `${response.name}`;
        }
        else if (type == "reset") {
            infoBox.innerText = '#';
        }
    }
    fetchProject(queryPk) {
        return __awaiter(this, void 0, void 0, function* () {
            let response = yield fetch(`${window.location.origin}/api/v1/projects/${queryPk}/exists/`);
            if (response.status == 200) {
                this.showInfo(yield response.json(), "success");
                projectFound = true;
            }
            else if (response.status == 206) {
                this.showInfo(yield response.json(), "warning");
                projectFound = false;
            }
        });
    }
    handleKeyup(event) {
        return __awaiter(this, void 0, void 0, function* () {
            queryPk = parseInt(event.target.innerText);
            if (isNaN(queryPk)) {
                this.showInfo("", "reset");
            }
            else {
                yield this.fetchProject(queryPk);
            }
        });
    }
    handleKeydown(event) {
        if (event.key == "Enter" && projectFound == true) {
            event.preventDefault();
            window.location.href = `${window.location.origin}/project-${queryPk}`;
        }
        else if (event.key == "Enter") {
            event.preventDefault();
        }
    }
}
window.customElements.define("sys-goto-project", SystoriGotoProject);
//# sourceMappingURL=goto_project.js.map