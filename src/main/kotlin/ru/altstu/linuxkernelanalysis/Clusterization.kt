package ru.altstu.linuxkernelanalysis

import kotlin.math.sqrt

/** Кластеризация сообщений */
class Clusterization(
    var clusterNumber: Int = 10,
    val nodes: List<WordMatcher.MessageInfo>
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
                    centroid = nodes[it].words
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
                diff += countDistance(lastCentroids[index], currentCentroids[index])
            if (diff == 0.0) isFinish = true
        }
    }

    /** Чистка нод каждого кластера */
    private fun clearClustersNodes() {
        for (cluster in clusters)
            cluster.clearNodes()
    }

    private val centroids: List<Map<WordMatcher.TokenInfo, Int>>
        get() {
            val centroids: MutableList<Map<WordMatcher.TokenInfo, Int>> = mutableListOf()

            for (cluster in clusters) {
                val centroid = cluster.centroid
                centroids.add(
                    mutableMapOf<WordMatcher.TokenInfo, Int>().apply {
                        centroid.forEach { entry -> this[entry.key] = entry.value }
                    }
                )
            }
            return centroids
        }

    private fun countDistance(firstMsg: Map<WordMatcher.TokenInfo, Int>, secondMsg: Map<WordMatcher.TokenInfo, Int>): Double {
        val compareWords = firstMsg + secondMsg
        var diff = 0.0

        for ((word, _) in compareWords) {
            val p1 = if (firstMsg.containsKey(word)) 1.0 else 0.0
            val p2 = if (secondMsg.containsKey(word)) 1.0 else 0.0
            diff += (p1 - p2) * (p1 - p2)
        }

        return sqrt(diff)
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
                distance = countDistance(node.words, cl.centroid)
                if (distance < min) {
                    min = distance
                    cluster = it
                }
            }
            clusters[cluster].addNode(node.words)
        }
    }

    /** Вычисляем на основе этих нод новые центры кластеров */
    private fun calculateCentroids() {
        // Проходимся по всем кластерам
        // Обходим все ноды в кластере и вычисляем новый "центр" кластера
    }
}