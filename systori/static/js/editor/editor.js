/**
 * This class extends KeyboardHandler to add a keyboard handler
 * to multi-line textareas. It allows the use of [Enter]+[Shift]
 * to enter new lines.
 */
class TextareaKeyboardHandler extends KeyboardHandler {
    /**
     * Handles the onKeyDown event.
     *
     * @param {KeyboardEvent} e - The keyboard event.
     * @param {TextInput} input - The TextInput instance.
     * @returns {boolean} Returns true if [Enter]+[Shift] is pressed, preventing other handlers; otherwise false.
     */
    onKeyDownEvent(e, input) {
        if (e.key === "Enter" && e.shiftKey) { // KeyCode.ENTER is typically 13 in JavaScript
            // don't run any other handlers
            return true;
        }
        return false;
    }
}