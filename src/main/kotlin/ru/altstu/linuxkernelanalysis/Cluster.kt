package ru.altstu.linuxkernelanalysis

class Cluster(
    var nodes: List<IMessange> = mutableListOf(),
    var distance:Double
) {


    fun merge(cluster: Cluster):Cluster{
        return Cluster(this.nodes + cluster.nodes ,this.distance(cluster))
    }

    fun getCentroid() : IMessange {
        return nodes.reduce { a, b -> a.getAverage(b) }
    }

    fun size():Int{
        return nodes.size
    }

    fun calculateSilhouetteCoefficient(clusters: List<Cluster>): Double {


        var totalSilhouette = 0.0
        var numPoints = 0

        for (cluster in clusters) {
            for (point in cluster.nodes) {
                val a = calculateAverageDistance(point, cluster.nodes)
                val b = calculateAverageDistance(point, findNearestCluster(point, clusters)?.nodes ?: emptyList())
                var s = (b - a) / maxOf(a, b)
                if(a == 0.0 && b == 0.0){
                    s = 0.0
                }
                totalSilhouette += s
                numPoints++
            }
        }

        return totalSilhouette / numPoints
    }

    private fun findNearestCluster(point: IMessange, clusters: List<Cluster>): Cluster? {
        var nearestCluster: Cluster? = null
        var minDistance = Double.MAX_VALUE

        for (cluster in clusters) {
            val distance = calculateAverageDistance(point, cluster.nodes)
            if (distance < minDistance) {
                minDistance = distance
                nearestCluster = cluster
            }
        }

        return nearestCluster
    }

    private fun calculateAverageDistance(point: IMessange, nodes: List<IMessange>): Double {
        val distance = nodes.filter { it != point }.map { point.getDistance(it) }.average()
        if(distance.isNaN()){
            return Double.MAX_VALUE
        }
        return nodes.filter { it != point }.map { point.getDistance(it) }.average()
    }

    fun distance(cluster: Cluster): Double {
        var totalDistance = 0.0
        for (item1 in this.nodes) {
            for (item2 in cluster.nodes) {
                totalDistance += item1.getDistance(item2)
            }
        }
        return totalDistance / (size() * cluster.size())
    }
}