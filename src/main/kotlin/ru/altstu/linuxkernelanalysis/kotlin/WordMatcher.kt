package ru.altstu.linuxkernelanalysis.kotlin

import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.pipeline.StanfordCoreNLP
import java.io.BufferedReader
import java.io.File
import java.io.FileReader
import java.lang.RuntimeException
import java.util.*
import java.util.concurrent.atomic.AtomicIntegerArray

// TODO: нужен рефактор после генерации
class WordMatcher(useTfIdf:Boolean): MessageMatcher {

    var uniqueWords: MutableList<String> = ArrayList()
    var weights: AtomicIntegerArray? = null
    var messages: MutableList<String> = ArrayList()
    var features: MutableList<HashMap<Int, Double>> = ArrayList()
    var sizes: MutableList<Double> = ArrayList()
    private val tfidf = useTfIdf


    override fun closestMessage(newMessage: String): String  =
        throw RuntimeException("Не используется тут")

    override fun addNewMessage(newMessage: String) {
        val props = Properties()
        props.setProperty("annotators", "tokenize, ssplit, pos, lemma")
        val pipeline = StanfordCoreNLP(props)
        val document = pipeline.process(newMessage)
        val sentences = document.get(CoreAnnotations.SentencesAnnotation::class.java)
        for (sentence in sentences) {
            val tokens = sentence.get(CoreAnnotations.TokensAnnotation::class.java)
            for (token in tokens) {
                val word = token.get(CoreAnnotations.TextAnnotation::class.java)
                val lemma = token.get(CoreAnnotations.LemmaAnnotation::class.java)
                println("$word - $lemma")
            }
        }

        //val newMsg = newMessage.lowercase(Locale.getDefault()).trim {it <= ' '}
        //val words = newMsg.split("[ !\"\\#$%&'()*+,-./:;<=>?@\\[\\]^_`{|}~]+".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
        //val feature = HashMap<Int, Double>()
        //var sz = 0.0
        //for (word in words) if (word.trim { it <= ' ' } !== "") {
        //    var rightWord: String? = word
        //    if (engWords.containsKey(word)) {
        //        // we have this word in the English dict
        //        rightWord = engWords[word]
        //    }
        //    // add a word to the all words collection
        //    if (!uniqueWords!!.contains(rightWord)) {
        //        uniqueWords!!.add(rightWord)
        //    }
        //    val pos = uniqueWords!!.indexOf(rightWord) // number of word in the list of all words
        //    feature[pos] = 1.0
        //    sz += 1.0
        //}
        //if (sz > 0 && !messages.contains(newMsg)) {
        //    messages.add(newMsg)
        //    features.add(feature)
        //    sizes.add(Math.sqrt(sz))
        //}
    }

    @Throws(InterruptedException::class)
    override fun buildMessageDistances() {
        if (tfidf) {
            val d = uniqueWords.size
            // calculate idfs
            val idfs = DoubleArray(d)
            for (w in 0 until d) {
                var idf = 0
                for (feature in features) {
                    if (feature.containsKey(w)) idf++
                }
                idfs[w] = Math.log(1.0 * d / idf)
            }
            // calculate tf and fix the vectors
            var f = 0
            for (feature in features) {
                var newSz = 0.0
                val tf = 1.0 / feature.size
                for (k in feature.keys) {
                    val newEl = feature[k]!! / (tf * idfs[k])
                    feature[k] = newEl
                    newSz += newEl * newEl
                }
                sizes[f++] = Math.sqrt(newSz)
            }
        }


        println("calculating distances...")
        weights = AtomicIntegerArray(messages.size) //for each message we will store its weight
        val ws = Any()

        // iteration for all messages should be parallelized
        val cores = Runtime.getRuntime().availableProcessors()
        val msgLen = messages.size
        val threads = Vector<Thread>(cores)
        for (p in 0 until cores) {
            val startI = p * msgLen / cores
            val endI = if (p != cores - 1) startI + msgLen / cores else msgLen
            val myP = p
            val t = Thread {
                for (i in startI until endI) for (j in messages.indices) if (i != j) {
                    val vector1 = features[i]
                    val vector2 = features[j]
                    var diff = 0.0
                    for (f in uniqueWords!!.indices) {
                        var p1 = 0.0
                        if (vector1.containsKey(f)) p1 = vector1[f]!!
                        var p2 = 0.0
                        if (vector2.containsKey(f)) p2 = vector2[f]!!
                        diff += p1 * p2
                    }
                    diff /= sizes[i] * sizes[j]
                    diff = 1.0 - diff
                    //System.out.println("t=" + myP+ ") i = " + i + " diff '" + messages.get(i)+ "' vs '" + messages.get(j) + "' = " + diff);
                    if (diff < 0.7) {
                        weights!!.getAndIncrement(i) //[i]++;
                        weights!!.getAndIncrement(j)
                    }
                }
            }
            threads.add(t)
            t.start()
        }
        for (p in 0 until cores) {
            threads[p].join()
        }

        // sort msgs by the weights
        // do now finding max for top times (compl max*O(n))
        val top = 50 //todo: set top
        val relevantMsgs = Vector<String>(top)
        for (total in 0 until top) {
            var max = -1
            var maxI = 0
            for (i in 0 until weights!!.length()) if (weights!![i] > max) {
                maxI = i
                max = weights!![i]
            }
            relevantMsgs.add(messages[maxI] + " / " + weights!![maxI])
            weights!![maxI] = 0
        }
        // print
        for (msg in relevantMsgs) {
            println(msg)
        }
    }
}