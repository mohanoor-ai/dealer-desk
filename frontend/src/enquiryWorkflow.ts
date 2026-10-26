export const requestTypes=['Check availability','Arrange a viewing','Book a test drive','Vehicle details','Request a callback','Other'] as const;
export const suggestions:Record<string,string>={
 'Check availability':'Check vehicle availability and reply to the customer',
 'Arrange a viewing':'Agree a viewing date and confirm the appointment',
 'Book a test drive':'Check availability and arrange a test drive slot',
 'Vehicle details':'Check the requested vehicle information and reply',
 'Request a callback':'Call the customer using the supplied number',
 'Other':'Review the message and agree the next action'
};
