import 'dart:html';
import 'dart:convert';
import 'package:quiver/collection.dart';

bool search_request_fired = false;
bool attempt_made = false;
Storage localStorage = window.localStorage;
InputElement search_input;
ButtonElement search_clear;
List<int> searchMatches = [];
List<String> phaseFilter = [];
List<String> phaseOrder = [
    "prospective",
    "tendering",
    "planning",
    "executing",
    "settlement",
    "warranty",
    "finished"
];

void sortProjects(Event e) {
    if (e == null) return;
    Map<int, Element> lookup;
    Multimap<String, Element> multimap;
    var i = 0;

    SystoriSortButton btn = e.target;
    btn.activateExclusive();

    if (btn.type == 'id') {
        lookup = new Map.fromIterable(querySelectorAll('.tile'),
                key: (e) => int.parse(e.dataset['pk']), value: (e) => e);
    } else if (btn.type == 'name') {
        lookup = new Map.fromIterable(querySelectorAll('.tile'),
                key: (e) => e.dataset['name'], value: (e) => e);
    } else if (btn.type == 'phase') {
        multimap = new Multimap.fromIterable(querySelectorAll('.tile'),
                key: (e) => "${e.dataset['phase']}", value: (e) => e);
        lookup = new Map();
        for (var key in phaseOrder) {
            for (var element in multimap[key]) {
                lookup[i++] = element;
            }
        }
    }

    List<int> sorted_keys = lookup.keys.toList()
        ..sort();
    if (btn.reversed == true) {
        sorted_keys = sorted_keys.reversed.toList();
        btn.reversed = false;
    } else if (btn.reversed == false) {
        btn.reversed = true;
    }

    var last_moved = null;

    for (var key in sorted_keys) {
        if (last_moved == null) {
            last_moved = lookup[key];
            continue;
        }
        last_moved.insertAdjacentElement("afterend", lookup[key]);
        last_moved = lookup[key];
    }
}

void updatePhaseFilter(Event e) {
    if (e == null) return;
    SystoriPhaseButton btn = e.target;
    btn.updatePhaseFilter();
    localStorage['phaseFilter'] = JSON.encode(phaseFilter);
    filterProjects();
}

void getPhaseFilter() {
    phaseFilter =
            (querySelectorAll('sys-phase-button') as List<SystoriPhaseButton>)
                    .where((btn) => btn.visiblePhase)
                    .map((btn) => btn.phase)
                    .toList();
}

void setPhaseFilter() {
    for (SystoriPhaseButton btn in querySelectorAll('sys-phase-button')) {
        if (phaseFilter.contains(btn.phase)) continue;
        btn.hide();
    }
    filterProjects();
}

bool isProjectInPhases(Element project, List phases) {
    return phases.contains(project.dataset['phase']);
}

void searchProjectsApi([_]) {
    localStorage['search_input'] = search_input.value;

    if (search_input.value == '') {
        clearFilter();
        attempt_made = false;
        return;
    }

    search_clear.classes.remove('hidden');
    var url = '/project-search?search=${search_input.value}';

    if (search_request_fired == true) {
        attempt_made = true;
        return;
    }

    search_request_fired = true;
    HttpRequest.getString(url).then((result) {
        search_request_fired = false;
        searchMatches = JSON.decode(result)['projects'] as List<int>;
        filterProjects();
        if (attempt_made) {
            attempt_made = false;
            searchProjectsApi();
        }
    });
}

void filterProjects([_]) {
    SystoriWarningMessage warning = querySelector('sys-warning-message');
    warning.hideWarningMessage = true;

    var projects = querySelectorAll('.tile');
    projects.classes.add('hidden');
    for (var project in projects) {
        if (!searchMatches.contains(int.parse(project.dataset['pk']))) continue;
        if (!isProjectInPhases(project, phaseFilter)) continue;
        project.classes.remove('hidden');
    }

    warning.warnPhaseFilteredProjects(
            searchMatches.length -
                    querySelectorAll('.tile:not(.hidden)').length);
}

void clearFilter([_]) {
    search_input.value = "";
    localStorage['search_input'] = "";
    localStorage['phaseFilter'] = "";
    search_clear.classes.add('hidden');
    searchMatches = querySelectorAll('.tile')
            .map((project) => int.parse(project.dataset['pk']))
            .toList();
    filterProjects();
}

class SystoriPhaseButton extends HtmlElement {
    static final tag = 'sys-phase-button';

    String get phase => dataset['phase'];

    set phase(String phase) => dataset['phase'] = phase;

    bool get hidePhase => dataset['hide-phase'] == 'true';

    bool get visiblePhase => !this.hidePhase;

    set hidePhase(bool hidePhase) {
        hidePhase
                ? dataset['hide-phase'] = 'true'
                : dataset['hide-phase'] = 'false';
    }

    hide() {
        this.hidePhase = true;
        phaseFilter.remove(phase);
        this.classes.add('line_through');
    }

    show() {
        this.hidePhase = false;
        phaseFilter.add(phase);
        this.classes.remove('line_through');
    }

    updatePhaseFilter([Event e]) {
        phaseFilter.contains(phase) ? hide() : show();
    }

    SystoriPhaseButton.created() : super.created() {
        if (dataset.containsKey('phase')) phase = dataset['phase'];
    }

    factory SystoriPhaseButton() => new Element.tag(tag);
}

class SystoriSortButton extends HtmlElement {
    static final tag = 'sys-sort-button';

    String get type => dataset['type'];

    set type(String type) => dataset['type'] = type;

    bool get reversed => dataset['reversed'] == 'true';

    set reversed(bool reversed) {
        reversed ? dataset['reversed'] = 'true' : dataset['reversed'] = 'false';
    }

    bool get active => this.classes.contains('active');

    set active(bool active) {
        active ? this.classes.add('active') : this.classes.remove('active');
    }

    activateExclusive() {
        List<SystoriSortButton> btns = (this.parentNode as DivElement)
                .querySelectorAll('sys-sort-button') as List<SystoriSortButton>;
        for (var btn in btns) {
            btn.active = false;
        }
        this.active = true;
        localStorage['sys-sort-button'] = this.type;
        localStorage['sys-sort-button-reversed'] = this.reversed.toString();
    }

    SystoriSortButton.created() : super.created() {
        if (dataset.containsKey('type')) type = dataset['type'];
        if (dataset.containsKey('reversed'))
            reversed = dataset['reversed'] == 'true';
    }

    factory SystoriSortButton() => new Element.tag(tag);
}

class SystoriProjectTile extends HtmlElement {
    static final tag = 'sys-project-tile';

    bool get hideProjectTile => this.classes.contains('hidden');

    set hideProjectTile(bool hideProjectTile) {
        hideProjectTile
                ? this.classes.add('hidden')
                : this.classes.remove('hidden');
    }

    SystoriProjectTile.created() : super.created() {}

    factory SystoriProjectTile() => new Element.tag(tag);
}

class SystoriWarningMessage extends HtmlElement {
    static final tag = 'sys-warning-message';

    warnPhaseFilteredProjects(int phaseFilteredProjects) {
        if (phaseFilteredProjects > 0) {
            this.children.first.text =
                    querySelector('#sys-phaseFilteredProjects-translated')
                            .text
                            .replaceAll(
                            new RegExp(r'(\$phaseFilteredProjects)'),
                            phaseFilteredProjects.toString());
            this.classes.remove('hidden');
        }
    }

    bool get hideWarningMessage => this.classes.contains('hidden');

    set hideWarningMessage(bool hideWarningMessage) {
        hideWarningMessage
                ? this.classes.add('hidden')
                : this.classes.remove('hidden');
    }

    SystoriWarningMessage.created() : super.created() {}

    factory SystoriWarningMessage() => new Element.tag(tag);
}

void loadLocalStorage() {
    querySelector('#filter-bar').classes.remove('hidden');
    querySelector('#tile-container').classes.remove('hidden');

    if (localStorage['search_input'] != "" &&
            localStorage['search_input'] != null) {
        search_input.value = localStorage['search_input'];
        search_clear.classes.remove('hidden');
        searchProjectsApi();
    } else {
        searchMatches = querySelectorAll('.tile')
                .map((project) => int.parse(project.dataset['pk']))
                .toList();
    }
    if (localStorage['phaseFilter'] != "" &&
            localStorage['phaseFilter'] != null) {
        phaseFilter = JSON.decode(localStorage['phaseFilter']) as List<String>;
        setPhaseFilter();
    } else {
        phaseFilter = [
            "prospective",
            "tendering",
            "planning",
            "executing",
            "settlement"
        ];
        setPhaseFilter();
    }
    if (localStorage['sys-sort-button'] != "" &&
            localStorage['sys-sort-button'] != null) {
        String type = localStorage['sys-sort-button'];
        SystoriSortButton btn =
        document.querySelector("sys-sort-button[data-type='$type']");
        btn.reversed = localStorage['sys-sort-button-reversed'] == "true";
        btn.click();
    }
}

void main() {
    document.registerElement('sys-phase-button', SystoriPhaseButton);
    document.registerElement('sys-project-tile', SystoriProjectTile);
    document.registerElement('sys-sort-button', SystoriSortButton);
    document.registerElement('sys-warning-message', SystoriWarningMessage);

    search_clear = querySelector('#search_clear');
    search_input = querySelector('#search_input');

    search_clear.onClick.listen(clearFilter);
    search_input.onInput.listen(searchProjectsApi);
    querySelectorAll('sys-sort-button').onClick.listen(sortProjects);
    querySelectorAll('sys-phase-button').onClick.listen(updatePhaseFilter);

    loadLocalStorage();
}
