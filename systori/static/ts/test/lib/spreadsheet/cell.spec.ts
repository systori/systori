import { Cell } from "@systori/lib/spreadsheet/cell";

describe("test", () => {
    it("can do stuff", () => {
        expect(new Cell("text", 1, 1).add(1, 2)).toBe(3);
    });
});
