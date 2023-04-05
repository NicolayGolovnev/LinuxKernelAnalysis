package ru.altstu.linuxkernelanalysis

class Cluster(
    var id: Int,
    var nodes: MutableList<IMessange> = mutableListOf(),
    var centroid:IMessange
) {
    fun addNode(node: IMessange) {
        this.nodes.add(node)
    }

    fun reCalculateCentroid() : IMessange{
        centroid = nodes.reduce{a, b -> a.getAverage(b)}
        return centroid
    }

    fun clearNodes() = nodes.clear()
}