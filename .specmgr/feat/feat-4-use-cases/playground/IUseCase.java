package biz.dfch.specmgr.models.usecase;

import java.time.LocalDate;
import java.util.List;

/**
 * Interface for a complete use case document based on Alistair Cockburn's template,
 * with Markdown source and YAML frontmatter.
 *
 * <p>A use case describes how a system interacts with external actors to achieve a specific goal.
 * This interface defines the contract for a structured use case document that includes:
 * <ul>
 *   <li><strong>Frontmatter:</strong> YAML metadata (id, version, status, created, updated dates)</li>
 *   <li><strong>Title:</strong> The name of the use case (e.g., "Buy Goods")</li>
 *   <li><strong>Characteristic Information:</strong> Context, actors, preconditions, success/failure conditions</li>
 *   <li><strong>Main Success Scenario:</strong> The "happy path" from trigger to goal completion</li>
 *   <li><strong>Extensions:</strong> Alternative flows triggered by specific conditions (optional)</li>
 *   <li><strong>Sub-Variations:</strong> Different technologies or methods for accomplishing steps (optional)</li>
 *   <li><strong>Open Issues:</strong> Questions and decisions awaiting resolution (optional)</li>
 *   <li><strong>Related Information:</strong> Notes and assumptions (optional)</li>
 * </ul>
 *
 * <p>All required sections must be present and valid; optional sections may be null.
 * Call {@link #validate()} to ensure the use case conforms to the schema.
 *
 * @see IFrontmatter
 * @see ICharacteristicInformation
 * @see IMainSuccessScenario
 * @see IExtensions
 * @see ISubVariations
 * @see IOpenIssues
 * @see IRelatedInformation
 */
public interface IUseCase {

    /**
     * Gets the frontmatter metadata.
     *
     * @return the frontmatter
     */
    IFrontmatter getFrontmatter();

    /**
     * Sets the frontmatter metadata.
     *
     * @param frontmatter the frontmatter to set
     */
    void setFrontmatter(IFrontmatter frontmatter);

    /**
     * Gets the use case title.
     *
     * @return the title
     */
    String getTitle();

    /**
     * Sets the use case title.
     *
     * @param title the title to set
     */
    void setTitle(String title);

    /**
     * Gets the characteristic information.
     *
     * @return the characteristic information
     */
    ICharacteristicInformation getCharacteristicInformation();

    /**
     * Sets the characteristic information.
     *
     * @param characteristicInformation the characteristic information to set
     */
    void setCharacteristicInformation(ICharacteristicInformation characteristicInformation);

    /**
     * Gets the main success scenario.
     *
     * @return the main success scenario
     */
    IMainSuccessScenario getMainSuccessScenario();

    /**
     * Sets the main success scenario.
     *
     * @param mainSuccessScenario the main success scenario to set
     */
    void setMainSuccessScenario(IMainSuccessScenario mainSuccessScenario);

    /**
     * Gets the extensions (alternative flows).
     *
     * @return the extensions, or null if not present
     */
    IExtensions getExtensions();

    /**
     * Sets the extensions (alternative flows).
     *
     * @param extensions the extensions to set
     */
    void setExtensions(IExtensions extensions);

    /**
     * Gets the sub-variations (technology/method alternatives).
     *
     * @return the sub-variations, or null if not present
     */
    ISubVariations getSubVariations();

    /**
     * Sets the sub-variations (technology/method alternatives).
     *
     * @param subVariations the sub-variations to set
     */
    void setSubVariations(ISubVariations subVariations);

    /**
     * Gets the open issues.
     *
     * @return the open issues, or null if not present
     */
    IOpenIssues getOpenIssues();

    /**
     * Sets the open issues.
     *
     * @param openIssues the open issues to set
     */
    void setOpenIssues(IOpenIssues openIssues);

    /**
     * Gets the related information.
     *
     * @return the related information, or null if not present
     */
    IRelatedInformation getRelatedInformation();

    /**
     * Sets the related information.
     *
     * @param relatedInformation the related information to set
     */
    void setRelatedInformation(IRelatedInformation relatedInformation);

    /**
     * Validates the use case against the schema.
     *
     * @throws ValidationException if validation fails
     */
    void validate() throws ValidationException;

    // ==================== Inner Interfaces ====================

    /**
     * Interface for YAML frontmatter metadata.
     */
    interface IFrontmatter {
        String getId();

        void setId(String id);

        String getVersion();

        void setVersion(String version);

        String getStatus();

        void setStatus(String status);

        LocalDate getCreated();

        void setCreated(LocalDate created);

        LocalDate getUpdated();

        void setUpdated(LocalDate updated);

        void validate() throws ValidationException;
    }

    /**
     * Interface for characteristic information.
     */
    interface ICharacteristicInformation {
        String getGoalInContext();

        void setGoalInContext(String goalInContext);

        String getScope();

        void setScope(String scope);

        String getLevel();

        void setLevel(String level);

        List<String> getPreconditions();

        void setPreconditions(List<String> preconditions);

        List<String> getSuccessEndCondition();

        void setSuccessEndCondition(List<String> successEndCondition);

        List<String> getFailedEndCondition();

        void setFailedEndCondition(List<String> failedEndCondition);

        String getPrimaryActor();

        void setPrimaryActor(String primaryActor);

        List<String> getSecondaryActors();

        void setSecondaryActors(List<String> secondaryActors);

        String getTrigger();

        void setTrigger(String trigger);

        String getFrequency();

        void setFrequency(String frequency);

        String getPriority();

        void setPriority(String priority);

        String getPerformanceTarget();

        void setPerformanceTarget(String performanceTarget);

        List<String> getChannelsToPrimaryActor();

        void setChannelsToPrimaryActor(List<String> channelsToPrimaryActor);

        List<String> getChannelsToSecondaryActors();

        void setChannelsToSecondaryActors(List<String> channelsToSecondaryActors);

        IRelatedUseCases getRelatedUseCases();

        void setRelatedUseCases(IRelatedUseCases relatedUseCases);

        void validate() throws ValidationException;
    }

    /**
     * Interface for related use cases.
     */
    interface IRelatedUseCases {
        String getSuperordinate();

        void setSuperordinate(String superordinate);

        List<String> getSubordinate();

        void setSubordinate(List<String> subordinate);

        void validate() throws ValidationException;
    }

    /**
     * Interface for main success scenario.
     */
    interface IMainSuccessScenario {
        List<IStep> getSteps();

        void setSteps(List<IStep> steps);

        void validate() throws ValidationException;
    }

    /**
     * Interface for a single step in a scenario.
     */
    interface IStep {
        Integer getNumber();

        void setNumber(Integer number);

        String getDescription();

        void setDescription(String description);

        void validate() throws ValidationException;
    }

    /**
     * Interface for extensions (alternative flows).
     */
    interface IExtensions {
        List<IExtension> getItems();

        void setItems(List<IExtension> items);

        void validate() throws ValidationException;
    }

    /**
     * Interface for a single extension.
     */
    interface IExtension {
        String getStepReference();

        void setStepReference(String stepReference);

        String getCondition();

        void setCondition(String condition);

        List<String> getActions();

        void setActions(List<String> actions);

        void validate() throws ValidationException;
    }

    /**
     * Interface for sub-variations (technology/method alternatives).
     */
    interface ISubVariations {
        List<ISubVariation> getItems();

        void setItems(List<ISubVariation> items);

        void validate() throws ValidationException;
    }

    /**
     * Interface for a single sub-variation.
     */
    interface ISubVariation {
        String getStepReference();

        void setStepReference(String stepReference);

        List<String> getVariations();

        void setVariations(List<String> variations);

        void validate() throws ValidationException;
    }

    /**
     * Interface for open issues.
     */
    interface IOpenIssues {
        List<String> getItems();

        void setItems(List<String> items);

        void validate() throws ValidationException;
    }

    /**
     * Interface for related information.
     */
    interface IRelatedInformation {
        List<String> getNotes();

        void setNotes(List<String> notes);

        List<String> getAssumptions();

        void setAssumptions(List<String> assumptions);

        void validate() throws ValidationException;
    }

    /**
     * Custom exception for validation errors.
     */
    class ValidationException extends RuntimeException {
        public ValidationException(String message) {
            super(message);
        }

        public ValidationException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
