package ru.altstu.linuxkernelanalysis

import java.io.IOException
import kotlin.math.sqrt


class WordMessange:IMessange {
    var tokens : MutableMap<WordMatcher.TokenInfo, Double> = hashMapOf()


    override fun getDistance(otherMessange: IMessange): Double {
        if(otherMessange is WordMessange) {
            val compareWords = this.tokens + otherMessange.tokens

            var diff = 0.0
            for ((word, _) in compareWords) {
                val p1 = if (this.tokens.containsKey(word)) this.tokens[word]!!.toDouble() else 0.0
                val p2 = if (otherMessange.tokens.containsKey(word)) otherMessange.tokens[word]!!.toDouble() else 0.0
                diff += (p1 - p2) * (p1 - p2)
            }

            return sqrt(diff)
        }
        throw IOException()
        //TODO pаеьенить нормальные исключения
    }

    override fun copy(): IMessange {
        val copy = WordMessange()
        copy.tokens = tokens.toMutableMap()
        return copy
    }

    override fun getNull(): IMessange {
        return WordMessange()
    }

    override fun toString(): String {
        return tokens.map { (a, b) -> a.word.toString() + ": " + b.toString() }.toString()
    }

    override fun getAverage(otherMessange: IMessange): IMessange {
        val average = WordMessange()

        if(otherMessange is WordMessange) {
            val compareWords = this.tokens + otherMessange.tokens

            var diff = 0.0
            for ((word, _) in compareWords) {
                val p1 = if (this.tokens.containsKey(word)) this.tokens[word]!! else 0.0
                val p2 = if (otherMessange.tokens.containsKey(word)) otherMessange.tokens[word]!! else 0.0
                average.tokens[word] = (p1 + p2) / 2
            }

            return average
        }
        throw IOException()
        //TODO pаеьенить нормальные исключения
    }
}