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
 * Represents a model extending HTML element, providing additional
 * properties and methods specific to the application's data model.
 * @extends HTMLElement
 */
class Model extends HTMLElement {
    /**
     * Constructs the Model object and initializes its properties.
     */
    constructor() {
        super();
        this.state = null; // Placeholder for ModelState, define this class separately
        this.inputs = {}; // Object for storing input elements
        this.editor = null; // Editor element

        if (!this.hasPK && !this.hasToken) {
            this.token = tokenGenerator.next(); // Ensure tokenGenerator is defined
        }

        if (this.children.length === 0) {
            const template = document.querySelector(`#${this.type}-template`);
            const clone = document.importNode(template.content, true);
            this.appendChild(clone);
        }

        this.editor = this.querySelector(":scope > .editor");
    }

    /**
     * Gets the type of the model, derived from the element's node name.
     * @returns {string} The model type.
     */
    get type() {
        return this.nodeName.toLowerCase().substring(4);
    }

    /**
     * Gets the child types of the model. To be overridden by subclasses.
     * @returns {Array<string>} An array of child types.
     */
    get childTypes() {
        return [];
    }

    /**
     * Determines if the model has child models.
     * @returns {boolean} True if the model has child models, false otherwise.
     */
    get hasChildModels() {
        return this.childTypes.some(childType => this.childrenOfType(childType).length > 0);
    }

    /**
     * Determines if the model has no child models.
     * @returns {boolean} True if the model has no child models, false otherwise.
     */
    get hasNoChildModels() {
        return !this.hasChildModels;
    }

    /**
     * Checks if the model has a primary key (PK).
     * @returns {boolean} True if the model has a PK, false otherwise.
     */
    get hasPK() {
        return this.dataset.hasOwnProperty('pk');
    }

    /**
     * Checks if the model has no primary key (PK).
     * @returns {boolean} True if the model has no PK, false otherwise.
     */
    get hasNoPK() {
        return !this.hasPK;
    }

    /**
     * Checks if the model has a token.
     * @returns {boolean} True if the model has a token, false otherwise.
     */
    get hasToken() {
        return this.dataset.hasOwnProperty('token');
    }

    /**
     * Checks if the model has no token.
     * @returns {boolean} True if the model has no token, false otherwise.
     */
    get hasNoToken() {
        return !this.hasToken;
    }

    /**
     * Gets the primary key (PK) of the model.
     * @returns {number|null} The primary key, or null if not set.
     */
    get pk() {
        return this.hasPK ? parseInt(this.dataset.pk) : null;
    }

    /**
     * Sets the primary key (PK) of the model.
     * @param {number} value - The primary key value to set.
     */
    set pk(value) {
        this.dataset.pk = value.toString();
    }

    /**
     * Gets the token of the model.
     * @returns {number|null} The token, or null if not set.
     */
    get token() {
        return this.hasToken ? parseInt(this.dataset.token) : null;
    }

    /**
     * Sets the token of the model.
     * @param {number} value - The token value to set.
     */
    set token(value) {
        this.dataset.token = value.toString();
    }

    /**
     * Finds children of a specific type within the model.
     * @param {string} childType - The type of child to find.
     * @returns {Array<Element>} An array of child elements of the specified type.
     */
    childrenOfType(childType) {
        // Implementation depends on how childType is defined and used
        // Placeholder implementation:
        return Array.from(this.children).filter(child => child.nodeName === `SYS-${childType.toUpperCase()}`);
    }

    /**
     * Placeholder getter for determining if the model can be saved.
     * To be overridden with specific logic.
     * @returns {boolean} True if the model can be saved, false otherwise.
     */
    get canSave() {
        return false; // Default implementation
    }

    // Other methods to be added...
}
