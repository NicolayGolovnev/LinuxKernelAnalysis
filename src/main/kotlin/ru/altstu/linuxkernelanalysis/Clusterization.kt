package ru.altstu.linuxkernelanalysis

import me.tongfei.progressbar.ProgressBar

/** Кластеризация сообщений */
class Clusterization(
    val nodes: List<IMessange>,
    var clusterNumber: Int = 10
) {
    val clusters = mutableListOf<Cluster>()

    fun calculateSilhouetteCoefficient(): Double {
        return clusters.map { it.calculateSilhouetteCoefficient(clusters)}.average()
    }


    fun getResult(): List<IMessange> {

        if(clusters.isEmpty()) {
            for (node in nodes) {
                clusters.add(Cluster(listOf(node), 0.0))
            }
        }

        val progressBar = ProgressBar("Clusters compress", (clusters.size - clusterNumber).toLong())


        while (clusters.size > clusterNumber) {
            progressBar.step()


            var minDistance = Double.MAX_VALUE
            var closestClusters = Pair(0, 1)
            for (i in 0 until clusters.size - 1) {
                for (j in i + 1 until clusters.size) {
                    val distance = clusters[i].distance(clusters[j])
                    if (distance < minDistance) {
                        minDistance = distance
                        closestClusters = Pair(i, j)
                    }
                    if(minDistance == 0.0){
                        break
                    }
                }

                if(minDistance == 0.0){
                    break
                }
            }

            val newCluster = clusters[closestClusters.first].merge(clusters[closestClusters.second])
            clusters.removeAt(closestClusters.second)
            clusters.removeAt(closestClusters.first)
            clusters.add(newCluster)
        }
        return clusters.map {it.getCentroid()}
    }


}