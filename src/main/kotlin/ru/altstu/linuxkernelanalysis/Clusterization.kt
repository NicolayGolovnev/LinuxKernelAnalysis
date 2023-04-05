package ru.altstu.linuxkernelanalysis

import kotlin.math.sqrt

/** Кластеризация сообщений */
class Clusterization(
    val nodes: List<IMessange>,
    var clusterNumber: Int = 10
    ) {
    /** Расстояние соседей между 2мя сообщениями */
    companion object {
        private const val NEIGHBORS_DISTANCE = 0.7
    }

    /** Кластеры */
    private val clusters: MutableList<Cluster> = mutableListOf()

    fun execute() {
        // Инициализация кластеров начальными значениями нод
        val messagesSize = nodes.size
        if (clusterNumber > messagesSize)
            clusterNumber = messagesSize

        repeat(clusterNumber) {
            clusters.add(
                Cluster(
                    id = it,
                    centroid = nodes[it].copy()
                )
            )
        }

        var isFinish = false

        /** Основной алгоритм */
        while (!isFinish) {
            /** Чистка нод каждого кластера */
            clearClustersNodes()

            /** Запоминаем старые центры кластеров */
            val lastCentroids = centroids

            /** Заполняем кластеры новыми подходящими нодами */
            assignCluster()

            /** Вычисляем на основе этих нод новые центры кластеров */
            calculateCentroids()

            /** Запомнили новые центры кластеров */
            val currentCentroids = centroids

            /**
             * Смотрим разницу между центрами кластеров.
             * Если разница минимальна (0.0), значит лучше уже не добиться -> искомые кластеры
             */
            var diff = 0.0
            for (index in currentCentroids.indices)
                diff += lastCentroids[index].getDistance(currentCentroids[index])
            if (diff == 0.0) isFinish = true
        }
    }

    /** Чистка нод каждого кластера */
    private fun clearClustersNodes() {
        for (cluster in clusters)
            cluster.clearNodes()
    }

    val centroids: List<IMessange>
        get() {
            return clusters.map {it.centroid}
        }


    /** Заполняем кластеры новыми подходящими нодами */
    private fun assignCluster() {
//        var min = NEIGHBORS_DISTANCE
        var min: Double
        var cluster = 0
        var distance = 0.0

        for (node in nodes) {
            // TODO возможно поставить максимум ?? возникнут проблемы с пустыми кластерами при NEIGHBORS_DISTANCE
            min = Double.MAX_VALUE
            repeat(clusterNumber) {
                val cl = clusters[it]
                distance = node.getDistance(cl.centroid)
                if (distance < min) {
                    min = distance
                    cluster = it
                }
            }
            clusters[cluster].addNode(node)
        }
    }

    /** Вычисляем на основе этих нод новые центры кластеров */
    private fun calculateCentroids() {
        clusters.map { it.reCalculateCentroid() }
    }
}