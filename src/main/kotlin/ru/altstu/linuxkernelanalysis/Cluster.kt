package ru.altstu.linuxkernelanalysis

class Cluster(
    var id: Int,
    var nodes: MutableList<Map<WordMatcher.TokenInfo, Int>> = mutableListOf(),
    var centroid: Map<WordMatcher.TokenInfo, Int>
) {
    fun addNode(node: Map<WordMatcher.TokenInfo, Int>) {
        this.nodes.add(node)
    }

    fun clearNodes() = nodes.clear()
}