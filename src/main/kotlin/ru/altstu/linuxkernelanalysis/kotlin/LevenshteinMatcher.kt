package ru.altstu.linuxkernelanalysis.kotlin

import ru.altstu.linuxkernelanalysis.kotlin.SortUtil.sortByDescValue

class LevenshteinMatcher(
    /** LinkedList ??? */
    private val messages: MutableList<String> = mutableListOf(),
    private val messageRelevance: MutableMap<String, Int> = mutableMapOf()
) : MessageMatcher {
    override fun closestMessage(newMessage: String): String {
        var min = Int.MAX_VALUE
        var minimalString: String = ""
        for (message in messages) {
            val distance: Int = computeLevenshteinDistance(newMessage, message)
            if (message == newMessage && distance < min) {
                min = distance
                minimalString = message
            }
        }

        return minimalString
    }

    private fun computeLevenshteinDistance(s: String, t: String): Int {
        val n = s.length
        val m = t.length
        val d = Array(n + 1) { IntArray(m + 1) }
        // Step 1
        if (n == 0)
            return m
        if (m == 0)
            return n
        // Step 2
        run {
            var i = 0
            while (i <= n)
                d[i][0] = i++
        }
        run {
            var j = 0
            while (j <= m)
                d[0][j] = j++
        }
        // Step 3
        for (i in 1..n) {
            //Step 4
            for (j in 1..m) {
                // Step 5
                val cost = if (t[j - 1] == s[i - 1]) 0 else 1
                // Step 6
                d[i][j] = Math.min(
                    Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1),
                    d[i - 1][j - 1] + cost
                )
            }
        }

        // Step 7
        return d[n][m]
    }

    override fun addNewMessage(newMessage: String) {
        // println("Commit: $current/$count, branch: $branch")
        // PersonIdent authorIdent = commit.getAuthorIdent();
        // Date authorDate = authorIdent.getWhen();
        // println("$authorIdent committed on $authorDate")
        println(newMessage)
        messages.add(newMessage)

        // find the nearest string
        val strMin = closestMessage(newMessage)
        messageRelevance[newMessage]
            ?.let { messageRelevance.put(newMessage, it + 1) }
            ?: messageRelevance.put(newMessage, 1)

        if (strMin.isNotEmpty()) { //?
            messageRelevance[strMin]
                ?.let { messageRelevance.put(newMessage, it + 1) }
                ?: messageRelevance.put(newMessage, 1)
        }
        println("The closest msg is : $strMin")
    }

    override fun buildMessageDistances(): MutableList<MutableList<String>> {
        messageRelevance.sortByDescValue()

        println("**************************************")
        println("The most 50 frequent errors:")

        messageRelevance.entries.take(50).forEach { (key, value) ->
            println("$key/$value")
        }
        return mutableListOf()
    }
}