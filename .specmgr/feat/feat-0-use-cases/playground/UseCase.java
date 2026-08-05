package biz.dfch.specmgr.models.usecase;

import java.time.LocalDate;
import java.util.List;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * A complete use case document based on Alistair Cockburn's template,
 * with Markdown source and YAML frontmatter.
 *
 * <p>This class provides a concrete implementation of {@link IUseCase} that models a structured
 * use case document. It manages all aspects of a use case including metadata, actors, scenarios,
 * and alternative flows.
 *
 * <p><strong>Structure:</strong>
 * <ul>
 *   <li><strong>Frontmatter:</strong> YAML metadata with id (uc-NNN), semantic version, status,
 *       and creation/update dates</li>
 *   <li><strong>Title:</strong> Single-line use case name (1-200 characters)</li>
 *   <li><strong>Characteristic Information:</strong> Metadata including goal, scope, level,
 *       actors, preconditions, success/failure conditions, trigger, frequency, priority,
 *       performance targets, communication channels, and related use cases</li>
 *   <li><strong>Main Success Scenario:</strong> Ordered steps (numbered 1, 2, 3, ...) describing
 *       the happy path from trigger to goal completion</li>
 *   <li><strong>Extensions:</strong> Alternative flows triggered at specific steps (e.g., "3a",
 *       "4b") with conditions and actions</li>
 *   <li><strong>Sub-Variations:</strong> Different technologies or methods for accomplishing
 *       specific steps (e.g., payment methods for step 10)</li>
 *   <li><strong>Open Issues:</strong> Unresolved questions and decisions</li>
 *   <li><strong>Related Information:</strong> Additional notes and assumptions</li>
 * </ul>
 *
 * <p><strong>Validation:</strong>
 * The {@link #validate()} method enforces schema constraints:
 * <ul>
 *   <li>Frontmatter: id matches "uc-[0-9]+", version is semantic, status is one of
 *       {draft, proposed, accepted, deprecated, superseded}</li>
 *   <li>Title: non-blank, 1-200 characters</li>
 *   <li>Characteristic Information: goal, scope, level, preconditions, success conditions,
 *       primary actor, and trigger are required; level must be one of {Summary, Primary task, Subfunction}</li>
 *   <li>Main Success Scenario: at least one step with number >= 1 and non-blank description</li>
 *   <li>Extensions: step references match "[0-9]+[a-z]?" (e.g., "3a"), conditions and actions required</li>
 *   <li>Sub-Variations: step references match "[0-9]+" (e.g., "7"), variations required</li>
 *   <li>Open Issues and Related Information: items must be non-blank if present</li>
 * </ul>
 *
 * <p><strong>Example:</strong>
 * <pre>
 * UseCase uc = new UseCase();
 * uc.setFrontmatter(new UseCase.Frontmatter("uc-001", "1.0.0", "draft",
 *     LocalDate.of(2026, 8, 5), LocalDate.of(2026, 8, 5)));
 * uc.setTitle("Buy Goods");
 * // ... set characteristic information, main success scenario, etc.
 * uc.validate(); // throws ValidationException if invalid
 * </pre>
 *
 * @see IUseCase
 * @see Frontmatter
 * @see CharacteristicInformation
 * @see MainSuccessScenario
 * @see Extensions
 * @see SubVariations
 * @see OpenIssues
 * @see RelatedInformation
 */
public class UseCase implements IUseCase {

    private Frontmatter frontmatter;
    private String title;
    private CharacteristicInformation characteristicInformation;
    private MainSuccessScenario mainSuccessScenario;
    private Extensions extensions;
    private SubVariations subVariations;
    private OpenIssues openIssues;
    private RelatedInformation relatedInformation;

    // Constructors
    public UseCase() {
    }

    public UseCase(Frontmatter frontmatter, String title,
                   CharacteristicInformation characteristicInformation,
                   MainSuccessScenario mainSuccessScenario) {
        this.frontmatter = frontmatter;
        this.title = title;
        this.characteristicInformation = characteristicInformation;
        this.mainSuccessScenario = mainSuccessScenario;
    }

    // Validation
    @Override
    public void validate() throws IUseCase.ValidationException {
        if (frontmatter == null) {
            throw new IUseCase.ValidationException("frontmatter is required");
        }
        frontmatter.validate();

        if (title == null || title.isBlank()) {
            throw new IUseCase.ValidationException("title is required and must not be empty");
        }
        if (title.length() < 1 || title.length() > 200) {
            throw new IUseCase.ValidationException("title must be between 1 and 200 characters");
        }

        if (characteristicInformation == null) {
            throw new IUseCase.ValidationException("characteristicInformation is required");
        }
        characteristicInformation.validate();

        if (mainSuccessScenario == null) {
            throw new IUseCase.ValidationException("mainSuccessScenario is required");
        }
        mainSuccessScenario.validate();

        if (extensions != null) {
            extensions.validate();
        }

        if (subVariations != null) {
            subVariations.validate();
        }

        if (openIssues != null) {
            openIssues.validate();
        }

        if (relatedInformation != null) {
            relatedInformation.validate();
        }
    }

    // Getters and Setters
    @Override
    public Frontmatter getFrontmatter() {
        return frontmatter;
    }

    @Override
    public void setFrontmatter(IFrontmatter frontmatter) {
        this.frontmatter = (Frontmatter) frontmatter;
    }

    @Override
    public String getTitle() {
        return title;
    }

    @Override
    public void setTitle(String title) {
        this.title = title;
    }

    @Override
    public CharacteristicInformation getCharacteristicInformation() {
        return characteristicInformation;
    }

    @Override
    public void setCharacteristicInformation(ICharacteristicInformation characteristicInformation) {
        this.characteristicInformation = (CharacteristicInformation) characteristicInformation;
    }

    @Override
    public MainSuccessScenario getMainSuccessScenario() {
        return mainSuccessScenario;
    }

    @Override
    public void setMainSuccessScenario(IMainSuccessScenario mainSuccessScenario) {
        this.mainSuccessScenario = (MainSuccessScenario) mainSuccessScenario;
    }

    @Override
    public Extensions getExtensions() {
        return extensions;
    }

    @Override
    public void setExtensions(IExtensions extensions) {
        this.extensions = (Extensions) extensions;
    }

    @Override
    public SubVariations getSubVariations() {
        return subVariations;
    }

    @Override
    public void setSubVariations(ISubVariations subVariations) {
        this.subVariations = (SubVariations) subVariations;
    }

    @Override
    public OpenIssues getOpenIssues() {
        return openIssues;
    }

    @Override
    public void setOpenIssues(IOpenIssues openIssues) {
        this.openIssues = (OpenIssues) openIssues;
    }

    @Override
    public RelatedInformation getRelatedInformation() {
        return relatedInformation;
    }

    @Override
    public void setRelatedInformation(IRelatedInformation relatedInformation) {
        this.relatedInformation = (RelatedInformation) relatedInformation;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        UseCase useCase = (UseCase) o;
        return Objects.equals(frontmatter, useCase.frontmatter) &&
                Objects.equals(title, useCase.title) &&
                Objects.equals(characteristicInformation, useCase.characteristicInformation) &&
                Objects.equals(mainSuccessScenario, useCase.mainSuccessScenario) &&
                Objects.equals(extensions, useCase.extensions) &&
                Objects.equals(subVariations, useCase.subVariations) &&
                Objects.equals(openIssues, useCase.openIssues) &&
                Objects.equals(relatedInformation, useCase.relatedInformation);
    }

    @Override
    public int hashCode() {
        return Objects.hash(frontmatter, title, characteristicInformation,
                mainSuccessScenario, extensions, subVariations, openIssues, relatedInformation);
    }

    @Override
    public String toString() {
        return "UseCase{" +
                "frontmatter=" + frontmatter +
                ", title='" + title + '\'' +
                ", characteristicInformation=" + characteristicInformation +
                ", mainSuccessScenario=" + mainSuccessScenario +
                ", extensions=" + extensions +
                ", subVariations=" + subVariations +
                ", openIssues=" + openIssues +
                ", relatedInformation=" + relatedInformation +
                '}';
    }

    // ==================== Inner Classes ====================

    /**
     * YAML frontmatter metadata for the use case document.
     */
    public static class Frontmatter implements IFrontmatter {
        private static final Pattern ID_PATTERN = Pattern.compile("^uc-[0-9]+$");
        private static final Pattern VERSION_PATTERN = Pattern.compile("^[0-9]+\\.[0-9]+\\.[0-9]+$");

        private String id;
        private String version;
        private String status;
        private LocalDate created;
        private LocalDate updated;

        public Frontmatter() {
        }

        public Frontmatter(String id, String version, String status, LocalDate created, LocalDate updated) {
            this.id = id;
            this.version = version;
            this.status = status;
            this.created = created;
            this.updated = updated;
        }

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (id == null || id.isBlank()) {
                throw new IUseCase.ValidationException("frontmatter.id is required");
            }
            if (!ID_PATTERN.matcher(id).matches()) {
                throw new IUseCase.ValidationException("frontmatter.id must match pattern '^uc-[0-9]+$'");
            }

            if (version == null || version.isBlank()) {
                throw new IUseCase.ValidationException("frontmatter.version is required");
            }
            if (!VERSION_PATTERN.matcher(version).matches()) {
                throw new IUseCase.ValidationException("frontmatter.version must match semantic versioning pattern");
            }

            if (status == null || status.isBlank()) {
                throw new IUseCase.ValidationException("frontmatter.status is required");
            }
            if (!isValidStatus(status)) {
                throw new IUseCase.ValidationException("frontmatter.status must be one of: draft, proposed, accepted, deprecated, superseded");
            }

            if (created == null) {
                throw new IUseCase.ValidationException("frontmatter.created is required");
            }

            if (updated == null) {
                throw new IUseCase.ValidationException("frontmatter.updated is required");
            }
        }

        private boolean isValidStatus(String status) {
            return status.equals("draft") || status.equals("proposed") ||
                    status.equals("accepted") || status.equals("deprecated") ||
                    status.equals("superseded");
        }

        // Getters and Setters
        @Override
        public String getId() {
            return id;
        }

        @Override
        public void setId(String id) {
            this.id = id;
        }

        @Override
        public String getVersion() {
            return version;
        }

        @Override
        public void setVersion(String version) {
            this.version = version;
        }

        @Override
        public String getStatus() {
            return status;
        }

        @Override
        public void setStatus(String status) {
            this.status = status;
        }

        @Override
        public LocalDate getCreated() {
            return created;
        }

        @Override
        public void setCreated(LocalDate created) {
            this.created = created;
        }

        @Override
        public LocalDate getUpdated() {
            return updated;
        }

        @Override
        public void setUpdated(LocalDate updated) {
            this.updated = updated;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Frontmatter that = (Frontmatter) o;
            return Objects.equals(id, that.id) &&
                    Objects.equals(version, that.version) &&
                    Objects.equals(status, that.status) &&
                    Objects.equals(created, that.created) &&
                    Objects.equals(updated, that.updated);
        }

        @Override
        public int hashCode() {
            return Objects.hash(id, version, status, created, updated);
        }

        @Override
        public String toString() {
            return "Frontmatter{" +
                    "id='" + id + '\'' +
                    ", version='" + version + '\'' +
                    ", status='" + status + '\'' +
                    ", created=" + created +
                    ", updated=" + updated +
                    '}';
        }
    }

    /**
     * All metadata and context about the use case.
     */
    public static class CharacteristicInformation implements ICharacteristicInformation {
        private String goalInContext;
        private String scope;
        private String level;
        private List<String> preconditions;
        private List<String> successEndCondition;
        private List<String> failedEndCondition;
        private String primaryActor;
        private List<String> secondaryActors;
        private String trigger;
        private String frequency;
        private String priority;
        private String performanceTarget;
        private List<String> channelsToPrimaryActor;
        private List<String> channelsToSecondaryActors;
        private RelatedUseCases relatedUseCases;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (goalInContext == null || goalInContext.isBlank()) {
                throw new IUseCase.ValidationException("characteristicInformation.goalInContext is required");
            }

            if (scope == null || scope.isBlank()) {
                throw new IUseCase.ValidationException("characteristicInformation.scope is required");
            }

            if (level == null || level.isBlank()) {
                throw new IUseCase.ValidationException("characteristicInformation.level is required");
            }
            if (!isValidLevel(level)) {
                throw new IUseCase.ValidationException("characteristicInformation.level must be one of: Summary, Primary task, Subfunction");
            }

            if (preconditions == null || preconditions.isEmpty()) {
                throw new IUseCase.ValidationException("characteristicInformation.preconditions is required and must have at least 1 item");
            }
            preconditions.forEach(p -> {
                if (p == null || p.isBlank()) {
                    throw new IUseCase.ValidationException("characteristicInformation.preconditions items must not be empty");
                }
            });

            if (successEndCondition == null || successEndCondition.isEmpty()) {
                throw new IUseCase.ValidationException("characteristicInformation.successEndCondition is required and must have at least 1 item");
            }
            successEndCondition.forEach(s -> {
                if (s == null || s.isBlank()) {
                    throw new IUseCase.ValidationException("characteristicInformation.successEndCondition items must not be empty");
                }
            });

            if (failedEndCondition != null) {
                failedEndCondition.forEach(f -> {
                    if (f == null || f.isBlank()) {
                        throw new IUseCase.ValidationException("characteristicInformation.failedEndCondition items must not be empty");
                    }
                });
            }

            if (primaryActor == null || primaryActor.isBlank()) {
                throw new IUseCase.ValidationException("characteristicInformation.primaryActor is required");
            }

            if (trigger == null || trigger.isBlank()) {
                throw new IUseCase.ValidationException("characteristicInformation.trigger is required");
            }

            if (relatedUseCases != null) {
                relatedUseCases.validate();
            }
        }

        private boolean isValidLevel(String level) {
            return level.equals("Summary") || level.equals("Primary task") || level.equals("Subfunction");
        }

        // Getters and Setters
        @Override
        public String getGoalInContext() {
            return goalInContext;
        }

        @Override
        public void setGoalInContext(String goalInContext) {
            this.goalInContext = goalInContext;
        }

        @Override
        public String getScope() {
            return scope;
        }

        @Override
        public void setScope(String scope) {
            this.scope = scope;
        }

        @Override
        public String getLevel() {
            return level;
        }

        @Override
        public void setLevel(String level) {
            this.level = level;
        }

        @Override
        public List<String> getPreconditions() {
            return preconditions;
        }

        @Override
        public void setPreconditions(List<String> preconditions) {
            this.preconditions = preconditions;
        }

        @Override
        public List<String> getSuccessEndCondition() {
            return successEndCondition;
        }

        @Override
        public void setSuccessEndCondition(List<String> successEndCondition) {
            this.successEndCondition = successEndCondition;
        }

        @Override
        public List<String> getFailedEndCondition() {
            return failedEndCondition;
        }

        @Override
        public void setFailedEndCondition(List<String> failedEndCondition) {
            this.failedEndCondition = failedEndCondition;
        }

        @Override
        public String getPrimaryActor() {
            return primaryActor;
        }

        @Override
        public void setPrimaryActor(String primaryActor) {
            this.primaryActor = primaryActor;
        }

        @Override
        public List<String> getSecondaryActors() {
            return secondaryActors;
        }

        @Override
        public void setSecondaryActors(List<String> secondaryActors) {
            this.secondaryActors = secondaryActors;
        }

        @Override
        public String getTrigger() {
            return trigger;
        }

        @Override
        public void setTrigger(String trigger) {
            this.trigger = trigger;
        }

        @Override
        public String getFrequency() {
            return frequency;
        }

        @Override
        public void setFrequency(String frequency) {
            this.frequency = frequency;
        }

        @Override
        public String getPriority() {
            return priority;
        }

        @Override
        public void setPriority(String priority) {
            this.priority = priority;
        }

        @Override
        public String getPerformanceTarget() {
            return performanceTarget;
        }

        @Override
        public void setPerformanceTarget(String performanceTarget) {
            this.performanceTarget = performanceTarget;
        }

        @Override
        public List<String> getChannelsToPrimaryActor() {
            return channelsToPrimaryActor;
        }

        @Override
        public void setChannelsToPrimaryActor(List<String> channelsToPrimaryActor) {
            this.channelsToPrimaryActor = channelsToPrimaryActor;
        }

        @Override
        public List<String> getChannelsToSecondaryActors() {
            return channelsToSecondaryActors;
        }

        @Override
        public void setChannelsToSecondaryActors(List<String> channelsToSecondaryActors) {
            this.channelsToSecondaryActors = channelsToSecondaryActors;
        }

        @Override
        public RelatedUseCases getRelatedUseCases() {
            return relatedUseCases;
        }

        @Override
        public void setRelatedUseCases(IRelatedUseCases relatedUseCases) {
            this.relatedUseCases = (RelatedUseCases) relatedUseCases;
        }

        @Override
        public String toString() {
            return "CharacteristicInformation{" +
                    "goalInContext='" + goalInContext + '\'' +
                    ", scope='" + scope + '\'' +
                    ", level='" + level + '\'' +
                    ", primaryActor='" + primaryActor + '\'' +
                    ", trigger='" + trigger + '\'' +
                    '}';
        }
    }

    /**
     * Links to parent and child use cases.
     */
    public static class RelatedUseCases implements IRelatedUseCases {
        private String superordinate;
        private List<String> subordinate;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (subordinate != null) {
                subordinate.forEach(s -> {
                    if (s == null || s.isBlank()) {
                        throw new IUseCase.ValidationException("relatedUseCases.subordinate items must not be empty");
                    }
                });
            }
        }

        @Override
        public String getSuperordinate() {
            return superordinate;
        }

        @Override
        public void setSuperordinate(String superordinate) {
            this.superordinate = superordinate;
        }

        @Override
        public List<String> getSubordinate() {
            return subordinate;
        }

        @Override
        public void setSubordinate(List<String> subordinate) {
            this.subordinate = subordinate;
        }

        @Override
        public String toString() {
            return "RelatedUseCases{" +
                    "superordinate='" + superordinate + '\'' +
                    ", subordinate=" + subordinate +
                    '}';
        }
    }

    /**
     * The happy path: steps from trigger to goal completion.
     */
    public static class MainSuccessScenario implements IMainSuccessScenario {
        private List<Step> steps;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (steps == null || steps.isEmpty()) {
                throw new IUseCase.ValidationException("mainSuccessScenario.steps is required and must have at least 1 item");
            }
            steps.forEach(Step::validate);
        }

        @Override
        public List<Step> getSteps() {
            return steps;
        }

        @Override
        public void setSteps(List<IStep> steps) {
            this.steps = (List<Step>) (List<?>) steps;
        }

        @Override
        public String toString() {
            return "MainSuccessScenario{" +
                    "steps=" + steps +
                    '}';
        }
    }

    /**
     * A single action or interaction in a scenario.
     */
    public static class Step implements IStep {
        private Integer number;
        private String description;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (number == null || number < 1) {
                throw new IUseCase.ValidationException("step.number is required and must be >= 1");
            }

            if (description == null || description.isBlank()) {
                throw new IUseCase.ValidationException("step.description is required and must not be empty");
            }
        }

        @Override
        public Integer getNumber() {
            return number;
        }

        @Override
        public void setNumber(Integer number) {
            this.number = number;
        }

        @Override
        public String getDescription() {
            return description;
        }

        @Override
        public void setDescription(String description) {
            this.description = description;
        }

        @Override
        public String toString() {
            return "Step{" +
                    "number=" + number +
                    ", description='" + description + '\'' +
                    '}';
        }
    }

    /**
     * Alternative flows that still result in success.
     */
    public static class Extensions implements IExtensions {
        private List<Extension> items;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (items == null || items.isEmpty()) {
                throw new IUseCase.ValidationException("extensions.items is required and must have at least 1 item");
            }
            items.forEach(Extension::validate);
        }

        @Override
        public List<Extension> getItems() {
            return items;
        }

        @Override
        public void setItems(List<IExtension> items) {
            this.items = (List<Extension>) (List<?>) items;
        }

        @Override
        public String toString() {
            return "Extensions{" +
                    "items=" + items +
                    '}';
        }
    }

    /**
     * An alternative flow triggered by a condition at a specific step.
     */
    public static class Extension implements IExtension {
        private static final Pattern STEP_REF_PATTERN = Pattern.compile("^[0-9]+[a-z]?$");

        private String stepReference;
        private String condition;
        private List<String> actions;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (stepReference == null || stepReference.isBlank()) {
                throw new IUseCase.ValidationException("extension.stepReference is required");
            }
            if (!STEP_REF_PATTERN.matcher(stepReference).matches()) {
                throw new IUseCase.ValidationException("extension.stepReference must match pattern '^[0-9]+[a-z]?$'");
            }

            if (condition == null || condition.isBlank()) {
                throw new IUseCase.ValidationException("extension.condition is required");
            }

            if (actions == null || actions.isEmpty()) {
                throw new IUseCase.ValidationException("extension.actions is required and must have at least 1 item");
            }
            actions.forEach(a -> {
                if (a == null || a.isBlank()) {
                    throw new IUseCase.ValidationException("extension.actions items must not be empty");
                }
            });
        }

        @Override
        public String getStepReference() {
            return stepReference;
        }

        @Override
        public void setStepReference(String stepReference) {
            this.stepReference = stepReference;
        }

        @Override
        public String getCondition() {
            return condition;
        }

        @Override
        public void setCondition(String condition) {
            this.condition = condition;
        }

        @Override
        public List<String> getActions() {
            return actions;
        }

        @Override
        public void setActions(List<String> actions) {
            this.actions = actions;
        }

        @Override
        public String toString() {
            return "Extension{" +
                    "stepReference='" + stepReference + '\'' +
                    ", condition='" + condition + '\'' +
                    ", actions=" + actions +
                    '}';
        }
    }

    /**
     * Different technologies or methods for accomplishing a step.
     */
    public static class SubVariations implements ISubVariations {
        private List<SubVariation> items;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (items == null || items.isEmpty()) {
                throw new IUseCase.ValidationException("subVariations.items is required and must have at least 1 item");
            }
            items.forEach(SubVariation::validate);
        }

        @Override
        public List<SubVariation> getItems() {
            return items;
        }

        @Override
        public void setItems(List<ISubVariation> items) {
            this.items = (List<SubVariation>) (List<?>) items;
        }

        @Override
        public String toString() {
            return "SubVariations{" +
                    "items=" + items +
                    '}';
        }
    }

    /**
     * Alternative ways to perform a specific step (e.g., payment methods).
     */
    public static class SubVariation implements ISubVariation {
        private static final Pattern STEP_REF_PATTERN = Pattern.compile("^[0-9]+$");

        private String stepReference;
        private List<String> variations;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (stepReference == null || stepReference.isBlank()) {
                throw new IUseCase.ValidationException("subVariation.stepReference is required");
            }
            if (!STEP_REF_PATTERN.matcher(stepReference).matches()) {
                throw new IUseCase.ValidationException("subVariation.stepReference must match pattern '^[0-9]+$'");
            }

            if (variations == null || variations.isEmpty()) {
                throw new IUseCase.ValidationException("subVariation.variations is required and must have at least 1 item");
            }
            variations.forEach(v -> {
                if (v == null || v.isBlank()) {
                    throw new IUseCase.ValidationException("subVariation.variations items must not be empty");
                }
            });
        }

        @Override
        public String getStepReference() {
            return stepReference;
        }

        @Override
        public void setStepReference(String stepReference) {
            this.stepReference = stepReference;
        }

        @Override
        public List<String> getVariations() {
            return variations;
        }

        @Override
        public void setVariations(List<String> variations) {
            this.variations = variations;
        }

        @Override
        public String toString() {
            return "SubVariation{" +
                    "stepReference='" + stepReference + '\'' +
                    ", variations=" + variations +
                    '}';
        }
    }

    /**
     * Questions and decisions awaiting resolution.
     */
    public static class OpenIssues implements IOpenIssues {
        private List<String> items;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (items == null || items.isEmpty()) {
                throw new IUseCase.ValidationException("openIssues.items is required and must have at least 1 item");
            }
            items.forEach(i -> {
                if (i == null || i.isBlank()) {
                    throw new IUseCase.ValidationException("openIssues.items must not be empty");
                }
            });
        }

        @Override
        public List<String> getItems() {
            return items;
        }

        @Override
        public void setItems(List<String> items) {
            this.items = items;
        }

        @Override
        public String toString() {
            return "OpenIssues{" +
                    "items=" + items +
                    '}';
        }
    }

    /**
     * Additional context, notes, and assumptions.
     */
    public static class RelatedInformation implements IRelatedInformation {
        private List<String> notes;
        private List<String> assumptions;

        @Override
        public void validate() throws IUseCase.ValidationException {
            if (notes != null) {
                notes.forEach(n -> {
                    if (n == null || n.isBlank()) {
                        throw new IUseCase.ValidationException("relatedInformation.notes items must not be empty");
                    }
                });
            }

            if (assumptions != null) {
                assumptions.forEach(a -> {
                    if (a == null || a.isBlank()) {
                        throw new IUseCase.ValidationException("relatedInformation.assumptions items must not be empty");
                    }
                });
            }
        }

        @Override
        public List<String> getNotes() {
            return notes;
        }

        @Override
        public void setNotes(List<String> notes) {
            this.notes = notes;
        }

        @Override
        public List<String> getAssumptions() {
            return assumptions;
        }

        @Override
        public void setAssumptions(List<String> assumptions) {
            this.assumptions = assumptions;
        }

        @Override
        public String toString() {
            return "RelatedInformation{" +
                    "notes=" + notes +
                    ", assumptions=" + assumptions +
                    '}';
        }
    }
}
