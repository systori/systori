export class Cell {
    constructor(
        public value: string,
        public row: number,
        public column: number,
    ) {}

    /**
     * add
     */
    public add(x: number, y: number): number {
        return x + y;
    }
}
