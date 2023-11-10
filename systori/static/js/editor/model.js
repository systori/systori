class ModelState {
    /**
     * Creates an instance of the ModelState.
     * @param {Model} model - The Model instance associated with this state.
     */
    constructor(model) {
        this.model = model;
        this.committed = ModelState.initialCommitted(model);
        this.pending = null;
    }

    /**
     * Returns true if there is a pending save operation.
     * @returns {boolean}
     */
    get isSaving() {
        return this.pending !== null;
    }

    /**
     * Prepares the object for a save operation, calculating the delta of changes.
     * @returns {Object} The pending changes.
     */
    save() {
        if (this.pending !== null) throw new Error('Save operation already pending');
        this.pending = this.delta;
        return this.pending;
    }

    /**
     * Commits the pending changes to the committed state.
     */
    commit() {
        if (this.pending === null) throw new Error('No pending changes to commit');
        Object.assign(this.committed, this.pending);
        this.pending = null;
    }

    /**
     * Rolls back any pending changes.
     */
    rollback() {
        if (this.pending === null) throw new Error('No pending changes to rollback');
        this.pending = null;
    }

    /**
     * Checks if a field has changed compared to its committed value.
     * @param {string} field - The field to check.
     * @param {any} value - The value to compare against.
     * @returns {boolean} True if the field has changed.
     */
    isChanged(field, value) {
        if (this.pending !== null && this.pending.hasOwnProperty(field)) {
            return this.pending[field] !== value;
        }
        return this.committed[field] !== value;
    }

    /**
     * Computes the delta of changes between the current and committed states.
     * @returns {Object} The delta object.
     */
    get delta() {
        const result = {};
        ModelState.inputMap(this.model.inputs.values).forEach((key, value) => {
            if (this.isChanged(key, value)) result[key] = value;
        });
        return result;
    }

    /**
     * Generates an initial committed state based on the model's primary key and inputs.
     * @param {Model} model - The model instance.
     * @returns {Object} The initial committed state.
     */
    static initialCommitted(model) {
        return model.hasPK
            ? ModelState.inputMap(model.inputs.values)
            : Object.fromEntries(Object.entries(ModelState.inputMap(model.inputs.values)).map(([key]) => [key, '']));
    }

    /**
     * Converts an iterable of inputs into a map of key-value pairs.
     * @param {Iterable<Input>} inputs - The iterable of inputs.
     * @returns {Object} The resulting map.
     */
    static inputMap(inputs) {
        const result = {};
        for (const input of inputs) {
            Object.assign(result, input.values);
        }
        return result;
    }
}
class Token {
    constructor() {
        this._previous = 0;
    }

    /**
     * Generates the next unique token.
     * @returns {number} The next token.
     */
    next() {
        let token = Date.now(); // Get the current time in milliseconds
        if (token <= this._previous) {
            token = ++this._previous;
        } else {
            this._previous = token;
        }
        return token;
    }
}
/**
 * Represents a model in the editor.
 * @extends HtmlElement
 */
class Model extends HtmlElement {
    /**
     * @returns {string} The type of the model.
     */
    get type() {
        return this.nodeName.toLowerCase().substring(4);
    }

    /**
     * @returns {Array<string>} The types of the children.
     */
    get childTypes() {
        return [];
    }

    /**
     * @returns {boolean} Whether the model has child models.
     */
    get hasChildModels() {
        for (let childType of this.childTypes) {
            if (this.childrenOfType(childType).length > 0) {
                return true;
            }
        }
        return false;
    }

    /**
     * @returns {boolean} Whether the model has no child models.
     */
    get hasNoChildModels() {
        return !this.hasChildModels;
    }

    /**
     * @returns {boolean} Whether the model has a primary key.
     */
    get hasPK() {
        return this.dataset.hasOwnProperty('pk');
    }

    /**
     * @returns {boolean} Whether the model has no primary key.
     */
    get hasNoPK() {
        return !this.hasPK;
    }

    /**
     * @returns {boolean} Whether the model has a token.
     */
    get hasToken() {
        return this.dataset.hasOwnProperty('token');
    }

    /**
     * @returns {boolean} Whether the model has no token.
     */
    get hasNoToken() {
        return !this.hasToken;
    }

    /**
     * @returns {number|null} The primary key of the model.
     */
    get pk() {
        return this.hasPK ? parseInt(this.dataset['pk']) : null;
    }

    /**
     * @param {number} pk The primary key to set.
     */
    set pk(pk) {
        this.dataset['pk'] = pk.toString();
    }

    /**
     * @returns {number|null} The token of the model.
     */
    get token() {
        return this.hasToken ? parseInt(this.dataset['token']) : null;
    }

    /**
     * @param {number} token The token to set.
     */
    set token(token) {
        this.dataset['token'] = token.toString();
    }

    /**
     * @type {ModelState} The state of the model.
     */
    state;

    /**
     * @type {Object.<string, Input>} The inputs of the model.
     */
    inputs = {};

    /**
     * @type {HtmlElement} The editor of the model.
     */
    editor;

    /**
     * Creates a new model.
     */
    constructor() {
        super();
        if (this.hasNoPK && this.hasNoToken) this.token = tokenGenerator.next();
        if (this.children.length === 0) {
            let template = document.querySelector(`#${this.type}-template`);
            let clone = document.importNode(template.content, true);
            this.append(clone);
        }
        this.editor = this.querySelector(":scope>.editor");
    }

    /**
     * @returns {boolean} Whether the model can be saved.
     */
    get canSave() {
        throw new Error("Method 'canSave' must be implemented.");
    }

    /**
     * Attaches the model to the DOM.
     */
    attached() {
        if (!this._readyCalled) {
            this.ready();
            this.state = new ModelState(this);
            this._readyCalled = true;
        }
    }

    /**
     * @type {boolean} Whether the model is ready.
     */
    _readyCalled = false;

    /**
     * Prepares the model.
     */
    ready() { }

    /**
     * @param {string} field The field to get the view for.
     * @returns {HtmlElement} The view for the field.
     */
    getView(field) {
        return this.editor.querySelector(`.${field}`);
    }

    /**
     * @param {string} field The field to get the input for.
     * @returns {Input} The input for the field.
     */
    getInput(field) {
        let input = this.getView(field);
        if (!(input instanceof Input)) {
            throw new Error("Input is not an instance of Input.");
        }
        if (this.inputs.hasOwnProperty(input.name)) {
            throw new Error("Input already exists.");
        }
        this.inputs[input.name] = input;
        return input;
    }

    /**
     * @returns {boolean} Whether the model has changed.
     */
    get isChanged() {
        return Object.keys(this.state.delta).length > 0;
    }

    /**
     * @param {string} childType The type of the children to get.
     * @returns {Array<Model>} The children of the specified type.
     */
    childrenOfType(childType) {
        let NODE_NAME = `SYS-${childType.toUpperCase()}`;
        return Array.from(this.children).filter(child => child.nodeName === NODE_NAME);
    }

    /**
     * @returns {Object} The data to save.
     */
    save() {
        let data = (this.isChanged && this.canSave) ? { ...this.state.save() } : {};
        if (Object.keys(data).length > 0) {
            this.updateVisualState('saving');
        }
        for (let childType of this.childTypes) {
            let saveChildren = this.childrenOfType(childType)
                .map(child => child.save())
                .filter(childData => Object.keys(childData).length > 0);
            if (saveChildren.length > 0) {
                data[`${childType}s`] = saveChildren;
            }
        }
        if (Object.keys(data).length > 0) {
            if (this.hasPK) {
                data['pk'] = this.pk;
            } else {
                data['token'] = this.token;
            }
        }
        return data;
    }

    /**
     * Rolls back the model.
     */
    rollback() {
        this.updateVisualState('changed');
        if (this.state.isSaving) this.state.rollback();
        for (let childType of this.childTypes) {
            this.childrenOfType(childType).forEach(child => child.rollback());
        }
    }

    /**
     * @param {Object} result The result to commit.
     */
    commit(result) {
        this.updateVisualState('saved');
        if (this.hasNoPK) {
            this.pk = result['pk'];
            delete this.dataset['token'];
        }
        if (this.state.isSaving) this.state.commit();
        for (let childType of this.childTypes) {
            let listName = `${childType}s`;
            if (!result.hasOwnProperty(listName)) continue;
            for (let child of this.childrenOfType(childType)) {
                for (let childResult of result[listName]) {
                    if ((child.hasPK && childResult['pk'] === child.pk) ||
                        (child.hasNoPK && childResult['token'] === child.token)) {
                        child.commit(childResult);
                    }
                }
            }
        }
    }

    /**
     * Deletes the model.
     */
    delete() {
        if (this.hasPK) changeManager.delete(this.type, this.pk);
        this.remove();
    }

    /**
     * Checks whether the children have changed.
     */
    maybeChildrenChanged() {
        for (let childType of this.childTypes) {
            this.childrenOfType(childType).forEach(child => child.updateVisualState('changed'));
        }
    }

    /**
     * @param {string} state The state to update the visual state to.
     */
    updateVisualState(state) {
        switch (state) {
            case 'changed':
                if (!this.editor.classList.contains(state) && this.isChanged) {
                    this.editor.className = 'editor changed';
                }
                break;
            case 'saving':
                this.editor.className = 'editor saving';
                break;
            case 'saved':
                this.editor.className = 'editor';
                break;
        }
    }

    /**
     * @returns {Model|null} The first model above this model.
     */
    firstAbove() {
        let match;

        // try siblings
        match = this.previousElementSibling;
        if (match instanceof Model) {
            while (true) {
                let modelChildren = null;
                for (let childType of match.childTypes) {
                    if (match.childrenOfType(childType).length > 0) {
                        modelChildren = match.childrenOfType(childType);
                        break;
                    }
                }
                if (modelChildren === null) break;
                match = modelChildren[modelChildren.length - 1];
            }
            return match;
        }

        return this.parent instanceof Model ? this.parent : null;
    }

    /**
     * @returns {Model|null} The first model below this model.
     */
    firstBelow() {
        // check children
        for (let childType of this.childTypes) {
            for (let child of this.childrenOfType(childType)) {
                return child;
            }
        }
        // now try siblings
        if (this.nextElementSibling instanceof Model) {
            return this.nextElementSibling;
        }
        // visit the ancestors
        let ancestor = this.parent;
        while (ancestor instanceof Model) {
            let sibling = ancestor.nextElementSibling;
            if (sibling instanceof Model) {
                return sibling;
            }
            ancestor = ancestor.parent;
        }

        return null;
    }
}

