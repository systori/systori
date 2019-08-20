/**
 * @author Jordan Luyke <jordanluyke@gmail.com>
 */

export interface Multimap<K, V> {
    clear(): void;
    containsKey(key: K): boolean;
    containsValue(value: V): boolean;
    containsEntry(key: K, value: V): boolean;
    delete(key: K, value?: V): boolean;
    entries: MultimapEntry<K, V>[];
    get(key: K): V[];
    keys(): K[];
    put(key: K, value: V): MultimapEntry<K, V>[];
}

export class ArrayListMultimap<K, V> implements Multimap<K, V> {
    private _entries: MultimapEntry<K, V>[] = [];

    public clear(): void {
        this._entries = [];
    }

    public containsKey(key: K): boolean {
        return this._entries.filter(entry => entry.key == key).length > 0;
    }

    public containsValue(value: V): boolean {
        return this._entries.filter(entry => entry.value == value).length > 0;
    }

    public containsEntry(key: K, value: V): boolean {
        return (
            this._entries.filter(
                entry => entry.key == key && entry.value == value,
            ).length > 0
        );
    }

    public delete(key: K, value?: V): boolean {
        const temp = this._entries;
        this._entries = this._entries.filter(entry => {
            if (value) return entry.key != key || entry.value != value;
            return entry.key != key;
        });
        return temp.length != this._entries.length;
    }

    public get entries(): MultimapEntry<K, V>[] {
        return this._entries;
    }

    public get(key: K): V[] {
        return this._entries
            .filter(entry => entry.key == key)
            .map(entry => entry.value);
    }

    public keys(): K[] {
        return Array.from(new Set(this._entries.map(entry => entry.key)));
    }

    public put(key: K, value: V): MultimapEntry<K, V>[] {
        this._entries.push(new MultimapEntry(key, value));
        return this._entries;
    }
}

class MultimapEntry<K, V> {
    constructor(readonly key: K, readonly value: V) {}
}
