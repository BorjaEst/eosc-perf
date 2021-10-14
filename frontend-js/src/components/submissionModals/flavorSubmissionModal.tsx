import React, { ReactElement, useState } from 'react';
import { Modal, Toast } from 'react-bootstrap';
import { Site } from 'api';
import { FlavorSubmitForm } from 'components/forms/flavorSubmitForm';

export function FlavorSubmissionModal(props: {
    show: boolean;
    onHide: () => void;
    site: Site;
}): ReactElement {
    const [showSuccessToast, setShowSuccessToast] = useState(false);

    return (
        <>
            <Modal size="lg" show={props.show} onHide={props.onHide}>
                <Modal.Header closeButton>Add Site</Modal.Header>
                <Modal.Body>
                    <FlavorSubmitForm
                        site={props.site}
                        onSuccess={() => {
                            props.onHide();
                            setShowSuccessToast(true);
                        }}
                        onError={() => undefined}
                    />
                </Modal.Body>
            </Modal>
            <div style={{ position: 'fixed', bottom: 0, right: 0 }}>
                <Toast
                    show={showSuccessToast}
                    onClose={() => setShowSuccessToast(false)}
                    delay={5000}
                    autohide
                >
                    <Toast.Header>
                        <strong className="me-auto">eosc-perf</strong>
                    </Toast.Header>
                    <Toast.Body>Submission successful.</Toast.Body>
                </Toast>
            </div>
        </>
    );
}
