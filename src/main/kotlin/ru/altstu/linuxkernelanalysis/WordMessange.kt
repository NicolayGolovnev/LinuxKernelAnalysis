package ru.altstu.linuxkernelanalysis

import java.io.IOException
import kotlin.math.sqrt


class WordMessange:IMessange {
    companion object {
        var countDocument = 0
    }

    var tokens : MutableMap<WordMatcher.TokenInfo, Double> = hashMapOf()
    var tfIdf:Boolean = false
    private fun getMetric(token:WordMatcher.TokenInfo, count: Double):Double{
        if (tfIdf) {
            return (count / tokens.values.sum()) * (Companion.countDocument/token.documentCount)
        }
        return count
    }

    override fun getDistance(otherMessange: IMessange): Double {
        if(otherMessange is WordMessange) {
            val unionTokens = this.tokens + otherMessange.tokens
            val intersection = this.tokens.filter { otherMessange.tokens.containsKey(it.key) }
            return 1 - intersection.size / unionTokens.size.toDouble()
        }
        throw IOException()
    }

    override fun copy(): IMessange {
        val copy = WordMessange()
        copy.tokens = tokens.toMutableMap()
        return copy
    }

    override fun getZero(): IMessange {
        return WordMessange()
    }

    override fun toString(): String {
        return tokens.size.toString() + tokens.toList().sortedBy {
                (a, value) -> -getMetric(a,value)}.toMap().map{ (a, _) -> a.word}.toString()
    }

    override fun getAverage(otherMessange: IMessange): IMessange {
        val average = WordMessange()
        if(otherMessange is WordMessange) {
            val compareWords = this.tokens + otherMessange.tokens
            for ((word, _) in compareWords) {
                val p1 = if (this.tokens.containsKey(word))  getMetric(word, this.tokens[word]!!) else 0.0
                val p2 = if (otherMessange.tokens.containsKey(word))  getMetric(word, otherMessange.tokens[word]!!) else 0.0
                average.tokens[word] = (p1 + p2) / 2
            }
            average.tfIdf = false
            return average
        }
        throw IOException()
    }
}