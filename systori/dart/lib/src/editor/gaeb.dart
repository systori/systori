class GAEBHierarchyStructure {
    // Python version: apps/project/models.py

    final String structure;
    final List<int> zfill;

    int get maximum_depth => zfill.length - 2;

    GAEBHierarchyStructure(String structure):
            structure = structure,
            zfill = structure.split('.').map((s)=>s.length).toList();

    String _format(String position, int zfill) =>
        position.padLeft(zfill, '0');

    String formatTask(String position) =>
        _format(position, zfill[zfill.length-1]);

    String formatGroup(String position, int depth) =>
        _format(position, zfill[depth]);

    bool isValidDepth(int depth) =>
        0 <= depth && depth <= maximum_depth;

}
