package ru.altstu.linuxkernelanalysis

import org.eclipse.jgit.api.Git
import org.eclipse.jgit.diff.*
import org.eclipse.jgit.lib.Constants
import org.eclipse.jgit.lib.Repository
import org.eclipse.jgit.patch.FileHeader
import org.eclipse.jgit.revwalk.RevCommit
import org.eclipse.jgit.revwalk.RevWalk
import org.eclipse.jgit.util.io.DisabledOutputStream
import ru.altstu.linuxkernelanalysis.SortUtil.sortByDescValue
import java.io.IOException
import java.util.*

class RepositoryScanner(
    val msgMatcher: MessageMatcher,
    val repository: Repository,
    val startDate: Date,
    val endDate: Date
) {
    private val git: Git = Git(repository)

    private var gitPath: String? = null
    private var mapFileChanges: MutableMap<KeyFilePos, Int> = hashMapOf()
    private var mapFileNameChanges: MutableMap<String, Int> = hashMapOf()

    @Throws(IOException::class)
    fun detectChanges(parent: RevCommit, commit: RevCommit) {
        val diffFormatter = DiffFormatter(DisabledOutputStream.INSTANCE)
        diffFormatter.setRepository(repository)
        diffFormatter.setDiffComparator(RawTextComparator.DEFAULT)
        diffFormatter.isDetectRenames = true
        val diffs: List<DiffEntry> = diffFormatter.scan(parent.tree, commit.tree)

        for (diff in diffs) {
            val header: FileHeader = diffFormatter.toFileHeader(diff)
            val name = header.newPath //filename with changes
            if (gitPath != "" && name.startsWith(gitPath!!)) for (edit in header.toEditList()) {
                if (mapFileNameChanges.containsKey(name)) {
                    mapFileNameChanges[name] = 1
                } else {
                    mapFileNameChanges[name] = mapFileNameChanges[name]!! + 1
                }
                for (line in edit.endB..edit.beginB) {
                    val key = KeyFilePos(name, line)
                    if (mapFileChanges.containsKey(key)) {
                        mapFileChanges[key] = 1
                    } else {
                        mapFileChanges[key] = mapFileChanges[key]!! + 1
                    }
                }
            }
        }
    }

    fun isCommitInBranch(commit: RevCommit, branchName: String): Boolean {
        val walk = RevWalk(this.repository)

        val targetCommit: RevCommit = walk.parseCommit(
            repository.resolve(commit.name)
        )

        return repository.allRefs.entries.find { (key, value) ->
            key.startsWith(Constants.R_HEADS) &&
                    walk.isMergedInto(targetCommit, walk.parseCommit(value.objectId)) &&
                    branchName == value.name
        } != null
    }

    fun getCommits(): Iterable<RevCommit> {
        return if (gitPath == null)
            git.log().all().call()
        else
            git.log()
                .add(git.repository.resolve(Constants.HEAD))
                .addPath(gitPath).call()
    }

    fun analyze() {
        val branches = git.branchList().call()

        for (branch in branches) {
            val branchName = branch.name
            val commits = getCommits().filter { commit ->
                Date(commit.commitTime * 1000L).after(startDate) &&
                        Date(commit.commitTime * 1000L).before(endDate) &&
                        commit.parentCount > 0
            }

            for (commit in commits) {
                if (isCommitInBranch(commit, branchName)) {
                    val lines = commit.fullMessage
                        .split("\n".toRegex())
                        .dropLastWhile { it.isEmpty() }
                        .toTypedArray()
                    lines
                        .filter { line -> isFixMessage(line) }
                        .map { line -> msgMatcher.addNewMessage(line) }
                }
                detectChanges(commit.getParent(0), commit)
            }
            msgMatcher.buildMessageDistances()
        }

        mapFileNameChanges = mapFileNameChanges.sortByDescValue()

        for ((fileName, _) in mapFileNameChanges.entries) {
            val pairsList = mapFileChanges.entries
                .filter { (key, _) -> key.fileName == fileName }
                .map { (key, value) -> Pair(key.position, value) }
            pairsList.sortedBy { el -> el.second }
        }
    }

    fun isFixMessage(message: String): Boolean {
        return "fix" in message
    }
}