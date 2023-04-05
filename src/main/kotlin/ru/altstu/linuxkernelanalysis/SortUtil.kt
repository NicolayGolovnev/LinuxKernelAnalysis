package ru.altstu.linuxkernelanalysis

import java.util.*
import java.util.stream.Collectors

object SortUtil {
    // Sorts a map by the value (desc)
    // TODO: посмотреть, как можно сделать по-котлину
    fun MutableMap<String, Int>.sortByDescValue(): MutableMap<String, Int> =
        this.entries
            .stream()
            // ReverseComparator -> c2.compareTo(c1)
            .sorted(java.util.Map.Entry.comparingByValue(Collections.reverseOrder()))
            .collect(
                Collectors.toMap(
                    { (key, _) -> key },
                    { (_, value) -> value },
                    { e1: Int, _: Int -> e1 },
                    { LinkedHashMap() })
            )
}