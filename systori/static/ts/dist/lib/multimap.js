/**
 * @author Jordan Luyke <jordanluyke@gmail.com>
 */
export class ArrayListMultimap {
    constructor() {
        this._entries = [];
    }
    clear() {
        this._entries = [];
    }
    containsKey(key) {
        return this._entries.filter(entry => entry.key == key).length > 0;
    }
    containsValue(value) {
        return this._entries.filter(entry => entry.value == value).length > 0;
    }
    containsEntry(key, value) {
        return (this._entries.filter(entry => entry.key == key && entry.value == value).length > 0);
    }
    delete(key, value) {
        const temp = this._entries;
        this._entries = this._entries.filter(entry => {
            if (value)
                return entry.key != key || entry.value != value;
            return entry.key != key;
        });
        return temp.length != this._entries.length;
    }
    get entries() {
        return this._entries;
    }
    get(key) {
        return this._entries
            .filter(entry => entry.key == key)
            .map(entry => entry.value);
    }
    keys() {
        return Array.from(new Set(this._entries.map(entry => entry.key)));
    }
    put(key, value) {
        this._entries.push(new MultimapEntry(key, value));
        return this._entries;
    }
}
class MultimapEntry {
    constructor(key, value) {
        this.key = key;
        this.value = value;
    }
}
//# sourceMappingURL=multimap.js.map