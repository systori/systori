/**
 * Represents a sticky header.
 */
class StickyHeader {
    /**
     * Creates a StickyHeader instance.
     *
     * @param {Job} job - The Job instance associated with this header.
     */
    constructor(job) {
        /** @type {Job} */
        this.job = job;

        /** @type {boolean} */
        this.DEBUG = false;

        /** @type {number} */
        this.TOP = 52;

        /** @type {Array<Group>} */
        this.oldFixedStack = [];

        /** @type {Array<Group>} */
        this.oldSlidingStack = [];

        /** @type {HTMLElement} */
        this.ts = null;

        /** @type {HTMLElement} */
        this.bs = null;

        window.addEventListener('scroll', this.handleScroll.bind(this));
        // Bind the methods to the class instance
        this.updateSensorMarkers = this.updateSensorMarkers.bind(this);
        this.handleScroll = this.handleScroll.bind(this);

        if (this.DEBUG) {
            this.ts = document.createElement('div');
            this.ts.style.backgroundColor = 'green';
            this.bs = document.createElement('div');
            this.bs.style.backgroundColor = 'red';

            [this.ts, this.bs].forEach(s => {
                s.style.position = 'fixed';
                s.style.width = '1px';
                s.style.height = '2px';
                s.style.zIndex = '1000';
                this.job.append(s);
            });

            this.updateSensorMarkers();
        }
    }
    /**
     * Updates the positions of sensor markers.
     * @param {number} [bottom] - The bottom position for the sensor marker. Optional.
     */
    updateSensorMarkers(bottom) {
        if (this.DEBUG) {
            this.ts.style.top = `${this.TOP}px`;
            this.ts.style.left = `${this.job.offsetLeft - 2}px`;
            this.bs.style.left = `${this.job.offsetLeft - 2}px`;

            if (bottom !== undefined) {
                this.bs.style.top = `${bottom}px`;
            } else {
                this.bs.style.top = '0px';
            }
        }
    }
    /**
     * Calculates the total height of a stack of Group elements.
     * @param {Array<Group>} stack - An array of Group elements.
     * @returns {number} The total height of the stack.
     */
    stackHeight(stack) {
        let height = 0;
        for (let model of stack) {
            height += model.children[0].children[0].clientHeight;
        }
        return height;
    }
    /**
     * Handles the scroll event.
     * @param {Event} e - The event object.
     */
    handleScroll(e) {
        if (this.DEBUG) console.log('-'.repeat(10));

        let topElement = document.elementFromPoint(this.job.offsetLeft, this.TOP);
        let topGroup = this.findGroup(topElement);
        if (!topGroup) {
            this.drawStacks([], []);
            this.updateSensorMarkers();
            if (this.DEBUG) {
                console.log("Clearing header.");
                console.log('+'.repeat(10));
            }
            return;
        }

        let topStack = this.makeGroupStack(topGroup);
        let topStackHeight = this.stackHeight(topStack);

        if (this.DEBUG) console.log(`Top Sensor: ${topGroup.name.text}`);

        let middleSensor = Math.round(topStackHeight / 2) + this.TOP;
        let middleElement = document.elementFromPoint(this.job.offsetLeft, middleSensor);
        let middleGroup = topElement === middleElement ? topGroup : this.findGroup(middleElement);

        let bottomSensor = topStackHeight + this.TOP;
        let bottomElement = document.elementFromPoint(this.job.offsetLeft, bottomSensor);
        let bottomGroup = middleElement === bottomElement ? middleGroup : this.findGroup(bottomElement);

        if (this.DEBUG) console.log(`Btm Sensor: ${bottomGroup?.name?.text}`);

        if (topGroup === bottomGroup || (topGroup === middleGroup && !bottomGroup)) {
            if (this.DEBUG) {
                console.log(`Top: ${topStack.map(g => g.name.text).join(', ')}`);
                console.log('top == bottom');
            }
            this.drawStacks(topStack, []);
            this.updateSensorMarkers(bottomSensor);
        } else if (middleGroup !== topGroup && middleGroup !== bottomGroup) {
            if (this.DEBUG) console.log('using middle group as top');
            this.processStack(this.makeGroupStack(middleGroup));
        } else if (topGroup === bottomGroup.parent) {
            if (this.DEBUG) console.log('using bottom group as top');
            this.processStack(this.makeGroupStack(bottomGroup));
        } else {
            if (this.DEBUG) console.log('using top group');
            this.processStack(topStack, bottomGroup);
        }

        if (this.DEBUG) console.log('+'.repeat(10));
    }
    /**
     * Processes the top and bottom stacks, and merges them into fixed and sliding stacks.
     * @param {Array<Group>} topStack - The top stack of Group elements.
     * @param {Group} [bottomGroup] - The bottom Group element, optional.
     */
    processStack(topStack, bottomGroup) {
        let bottomSensor = this.stackHeight(topStack) + this.TOP;
        if (!bottomGroup) {
            bottomGroup = this.findGroup(document.elementFromPoint(this.job.offsetLeft, bottomSensor));
        }
        let bottomStack = this.makeGroupStack(bottomGroup);
        let fixed = [], sliding = [];

        this.mergeStacks(topStack, bottomStack, fixed, sliding);

        if (this.DEBUG) {
            console.log(`Top: ${topStack.map(g => g.name.text).join(', ')}`);
            console.log(`Btm: ${bottomStack.map(g => g.name.text).join(', ')}`);
            console.log(`Fixed: ${fixed.map(g => g.name.text).join(', ')}`);
            console.log(`Slide: ${sliding.map(g => g.name.text).join(', ')}`);
        }

        let slidingStart;
        if (sliding.length > 0) {
            let fixedBottom = fixed[fixed.length - 1].children[0].children[0]
                .getBoundingClientRect()
                .bottom;
            let rec = bottomGroup.children[0].getBoundingClientRect();
            slidingStart = Math.round(rec.top) - 1;
            if (fixedBottom >= slidingStart) {
                if (this.DEBUG) console.log('fixed = bottomStack');
                fixed = bottomStack;
            }
        }

        this.drawStacks(fixed, sliding, slidingStart);
        this.updateSensorMarkers(bottomSensor);
    }
    /**
     * Merges the top and bottom stacks into fixed and sliding stacks.
     * @param {Array<Group>} topStack - The top stack of Group elements.
     * @param {Array<Group>} bottomStack - The bottom stack of Group elements.
     * @param {Array<Group>} fixed - The fixed stack to populate.
     * @param {Array<Group>} sliding - The sliding stack to populate.
     */
    mergeStacks(topStack, bottomStack, fixed, sliding) {
        let longest = Math.max(topStack.length, bottomStack.length);
        for (let i = 0; i < longest; i++) {
            let topModel = i < topStack.length ? topStack[i] : null;
            let bottomModel = i < bottomStack.length ? bottomStack[i] : null;
            if (topModel === bottomModel) {
                fixed.push(topModel);
            } else {
                if (topModel !== null) {
                    sliding.unshift(topModel); // insert at beginning
                } else if (bottomModel !== null) {
                    fixed.push(bottomModel);
                }
            }
        }
    }
    /**
     * Draws the new fixed and sliding stacks, updating the position and appearance of elements.
     * @param {Array<Group>} newFixedStack - The new fixed stack of Group elements.
     * @param {Array<Group>} newSlidingStack - The new sliding stack of Group elements.
     * @param {number} [slidingStart] - The starting position for sliding elements, optional.
     */
    drawStacks(newFixedStack, newSlidingStack, slidingStart) {
        const concat = (arrays) => [].concat(...arrays);

        for (let group of concat([this.oldFixedStack, this.oldSlidingStack])) {
            if (!newFixedStack.includes(group) && !newSlidingStack.includes(group)) {
                let editor = group.children[0];
                let row = editor.children[0];
                if (row.classList.contains('sticky-header')) {
                    row.style.top = '';
                    row.style.width = '';
                    row.classList.remove('sticky-header');
                    editor.removeChild(editor.children[1]);
                    if (this.DEBUG) console.log(`"${group.name.text}" removeAt(1)`);
                    row.classList.remove('sliding');
                }
            }
        }

        for (let group of concat([newFixedStack, newSlidingStack])) {
            let editor = group.children[0];
            let row = editor.children[0];
            if (!row.classList.contains('sticky-header')) {
                if (this.DEBUG) console.log(`"${group.name.text}" insertBefore(document.createElement(div), ...)`);
                let spacer = document.createElement('div');
                spacer.style.height = `${row.clientHeight}px`;
                row.style.width = `${row.clientWidth}px`;
                row.classList.add('sticky-header');
                editor.insertBefore(spacer, editor.children[1]);
            }
        }

        let offset = this.TOP - 1;
        for (let model of newFixedStack) {
            let editor = model.children[0];
            let row = editor.children[0];
            row.style.top = `${offset}px`;
            offset += row.clientHeight - 1;
            row.classList.toggle('sliding', false);
        }

        for (let model of newSlidingStack) {
            let editor = model.children[0];
            let row = editor.children[0];
            slidingStart -= row.clientHeight;
            row.style.top = `${slidingStart}px`;
            row.classList.toggle('sliding', true);
        }

        this.oldFixedStack = newFixedStack;
        this.oldSlidingStack = newSlidingStack;
    }
    /**
     * Finds the closest Group element in the ancestor hierarchy of a given element.
     * @param {HTMLElement} element - The starting element to search from.
     * @returns {Group|null} The found Group element, or null if none is found.
     */
    findGroup(element) {
        while (element) {
            if (element instanceof Group) { // Group is a class extending HTMLElement
                return element;
            }
            element = element.parentElement;
        }
        return null;
    }
    /**
     * Creates a stack of Group elements starting from a specified Group and moving up its parent chain.
     * @param {Group} group - The starting Group element.
     * @returns {Array<Group>} An array representing the stack of Group elements.
     */
    makeGroupStack(group) {
        let newStack = [];
        if (group !== null) {
            newStack.unshift(group); // unshift is used to insert at the beginning of the array
            while (group !== null && !(group instanceof Job)) { // Checking if it's not an instance of Job
                group = group.parentElement;
                if (group instanceof Group) {
                    newStack.unshift(group);
                }
            }
        }
        return newStack;
    }
}