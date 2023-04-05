package ru.altstu.linuxkernelanalysis


class KeyFilePos(
    val fileName: String,
    val position: Int
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as KeyFilePos

        if (fileName != other.fileName) return false
        if (position != other.position) return false

        return true
    }

    /** Раньше было fileName.hashCode() ^ position.hashCode() */
    override fun hashCode(): Int {
        var result = fileName.hashCode()
        result = 31 * result + position.hashCode()
        return result
    }
}